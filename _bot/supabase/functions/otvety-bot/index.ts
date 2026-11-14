// Telegram-бот «Ответы»: inline-режим + личка + статистика в public.events.
// Секреты (Supabase → Edge Functions → Secrets): BOT_TOKEN, WEBHOOK_SECRET. Необязательно: BASE_URL.
// Первая настройка после секретов: открыть <url функции>?setup=<WEBHOOK_SECRET> — поставит вебхук и команды.
import fallback from "./answers.json" with { type: "json" };

import type { Answer } from "./search.ts";

const TOKEN = Deno.env.get("BOT_TOKEN") ?? "";
const SECRET = Deno.env.get("WEBHOOK_SECRET") ?? "";
const BASE = (Deno.env.get("BASE_URL") ?? "https://otvety.nerdstudio.dev/").replace(/\/?$/, "/");
const SB_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SB_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const FN_URL = `${SB_URL}/functions/v1/otvety-bot`;

// ---------- ответы: с сайта, кеш 10 минут; если сайт недоступен — копия, вшитая при деплое ----------
let answers: Answer[] = (fallback as Answer[]).slice().sort((a, b) => a.top - b.top);
let loadedAt = 0;
async function getAnswers(): Promise<Answer[]> {
  if (Date.now() - loadedAt < 10 * 60_000) return answers;
  loadedAt = Date.now();
  try {
    const r = await fetch(BASE + "answers.json", { signal: AbortSignal.timeout(1500) });
    if (r.ok) {
      const list = (await r.json()) as Answer[];
      if (Array.isArray(list) && list.length) answers = list.sort((a, b) => a.top - b.top);
    }
  } catch { /* остаёмся на текущем списке */ }
  return answers;
}

import { search } from "./search.ts";

// ---------- Telegram ----------
const tg = (method: string, body: unknown) =>
  fetch(`https://api.telegram.org/bot${TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(8000),
  }).then((r) => r.json());

let me: { username: string } | null = null;
async function botName(): Promise<string> {
  if (!me) me = (await tg("getMe", {})).result;
  return me?.username ?? "bot";
}

const pageUrl = (a: Answer) => `${BASE}${a.slug}/`;
const sameButton = (a: Answer) => ({
  text: "Ответить так же",
  switch_inline_query_chosen_chat: {
    query: a.word, allow_user_chats: true, allow_group_chats: true, allow_channel_chats: true,
  },
});
// Сообщение = ссылка на лендинг; Telegram рисует под ней большое превью из og.png.
const answerMessage = (a: Answer) => ({
  text: pageUrl(a),
  link_preview_options: { url: pageUrl(a), prefer_large_media: true },
  reply_markup: { inline_keyboard: [[sameButton(a)]] },
});

function inlineResult(a: Answer) {
  const m = answerMessage(a);
  return {
    type: "article",
    id: a.slug,
    title: a.word + a.dot,
    description: a.tag,
    thumbnail_url: `${BASE}${a.slug}/thumb.jpg`,
    thumbnail_width: 320,
    thumbnail_height: 168,
    input_message_content: { message_text: m.text, link_preview_options: m.link_preview_options },
    reply_markup: m.reply_markup,
  };
}

// ---------- статистика ----------
const enc = new TextEncoder();
let hmacKey: CryptoKey | null = null;
async function userHash(id?: number): Promise<string | null> {
  if (!id) return null;
  // Соль выводим из WEBHOOK_SECRET, чтобы не заводить отдельный секрет. Сам id нигде не сохраняется.
  hmacKey ??= await crypto.subtle.importKey("raw", enc.encode("otvety-user:" + SECRET), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", hmacKey, enc.encode(String(id))));
  return Array.from(sig.slice(0, 16), (b) => b.toString(16).padStart(2, "0")).join("");
}

async function log(type: string, userId: number | undefined, slug: string | null, query?: string) {
  try {
    await fetch(`${SB_URL}/rest/v1/events`, {
      method: "POST",
      headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, "Content-Type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({
        type, answer_slug: slug, query_text: query ? [...query].slice(0, 64).join("") : null, user_hash: await userHash(userId),
      }),
    });
  } catch (e) { console.error("log failed", e); }
}
// Не задерживаем ответ Telegram ради записи в базу.
const later = (p: Promise<unknown>) => {
  // deno-lint-ignore no-explicit-any
  const rt = (globalThis as any).EdgeRuntime;
  rt?.waitUntil ? rt.waitUntil(p) : p.catch(() => {});
};

// ---------- личка ----------
async function helpText(n: number) {
  const name = await botName();
  return `Отвечай одним словом — красиво.\n\nВ любом чате напиши @${name} и выбери ответ: «Да», «Нет», «У меня работает», «В пятницу не деплоим» и ещё ${n - 4}. В чат уйдёт ссылка с большой карточкой.\n\nИли нажми ответ ниже — пришлю сюда, отправишь кому надо.`;
}
const tryButton = { text: "Попробовать в чате", switch_inline_query: "" };
function grid(list: Answer[]) {
  const rows: unknown[][] = [[tryButton]];
  for (let i = 0; i < list.length; i += 2) {
    rows.push(list.slice(i, i + 2).map((a) => ({ text: a.word + a.dot, callback_data: "a:" + a.slug })));
  }
  return { inline_keyboard: rows };
}

// ---------- обработка апдейтов ----------
// deno-lint-ignore no-explicit-any
async function handle(u: any): Promise<unknown | null> {
  const list = await getAnswers();

  if (u.inline_query) {
    const q: string = u.inline_query.query ?? "";
    later(log("inline_query", u.inline_query.from?.id, null, q));
    const found = search(list, q).slice(0, 50);
    return {
      method: "answerInlineQuery",
      inline_query_id: u.inline_query.id,
      results: found.map(inlineResult),
      cache_time: 300,
      is_personal: false,
      button: { text: found.length ? "Как это работает" : "Ничего не нашлось — открыть список", start_parameter: "help" },
    };
  }

  if (u.chosen_inline_result) {
    const r = u.chosen_inline_result;
    later(log("chosen", r.from?.id, r.result_id, r.query));
    return null;
  }

  if (u.callback_query) {
    const c = u.callback_query;
    const a = list.find((x) => "a:" + x.slug === c.data);
    later(tg("answerCallbackQuery", { callback_query_id: c.id }));
    if (!a || !c.message) return null;
    later(log("dm", c.from?.id, a.slug));
    return { method: "sendMessage", chat_id: c.message.chat.id, ...answerMessage(a) };
  }

  const m = u.message;
  if (m && m.chat?.type === "private") {
    const isStart = typeof m.text === "string" && m.text.startsWith("/start");
    if (isStart) later(log("start", m.from?.id, null));
    return {
      method: "sendMessage",
      chat_id: m.chat.id,
      text: await helpText(list.length),
      reply_markup: grid(list), // первая строка — «Попробовать в чате», ниже все ответы
    };
  }
  return null;
}

// ---------- HTTP ----------
function sameSecret(a: string, b: string) {
  if (!a || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

async function setup() {
  const webhook = await tg("setWebhook", {
    url: FN_URL,
    secret_token: SECRET,
    allowed_updates: ["message", "inline_query", "chosen_inline_result", "callback_query"],
    drop_pending_updates: true,
  });
  const commands = await tg("setMyCommands", { commands: [{ command: "start", description: "Как пользоваться" }] });
  const db = await fetch(`${SB_URL}/rest/v1/events?select=id&limit=1`, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
  return { bot: "@" + (await botName()), webhook, commands, db: db.ok ? "ok" : `error ${db.status}`, base: BASE };
}

Deno.serve(async (req) => {
  if (!TOKEN || !SECRET) return new Response("BOT_TOKEN / WEBHOOK_SECRET not set", { status: 500 });
  const url = new URL(req.url);

  if (req.method === "GET") {
    const key = url.searchParams.get("setup");
    if (key !== null && sameSecret(key, SECRET)) {
      return Response.json(await setup());
    }
    return new Response("ok");
  }

  if (!sameSecret(req.headers.get("X-Telegram-Bot-Api-Secret-Token") ?? "", SECRET)) {
    return new Response("forbidden", { status: 403 });
  }

  try {
    const reply = await handle(await req.json());
    // Ответ прямо в теле вебхука — без лишнего запроса к Telegram.
    if (reply) return Response.json(reply);
  } catch (e) {
    console.error("update failed", e);
  }
  return new Response("ok");
});
