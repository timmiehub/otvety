// Telegram-бот «Ответы»: inline-режим + личка + статистика в public.events.
// Секрет (Supabase → Edge Functions → Secrets): BOT_TOKEN. Необязательно: BASE_URL.
// Вебхук бот ставит себе сам при запуске. Состояние: GET <url функции> → JSON со статусом.
import fallback from "./answers.json" with { type: "json" };

import type { Answer } from "./search.ts";

// trim: при вставке из буфера в секрет легко попадает перевод строки
const TOKEN = (Deno.env.get("BOT_TOKEN") ?? "").trim();
const enc = new TextEncoder();
// Секрет вебхука и соль для хеша пользователей выводим из токена: знает их только тот, у кого есть токен.
async function derive(label: string): Promise<string> {
  const key = await crypto.subtle.importKey("raw", enc.encode(TOKEN), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(label)));
  return Array.from(sig, (b) => b.toString(16).padStart(2, "0")).join("");
}
const SECRET = TOKEN ? await derive("otvety-webhook") : "";
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

import { GROUPS, search } from "./search.ts";

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
// Версия карточек: при смене картинок поднять — Telegram заново заберёт превью (он кеширует его по адресу ссылки).
const CARD_V = "2";
const shareUrl = (a: Answer) => `${pageUrl(a)}?v=${CARD_V}`;
// Кнопка под карточкой ведёт в бота; start-параметр говорит, с какой карточки пришли.
const sameButton = (a: Answer, bot: string) => ({ text: "Ответить так же", url: `https://t.me/${bot}?start=a_${a.slug}` });
// Сообщение = слово ответа, оформленное ссылкой на лендинг; под ним Telegram рисует большое превью из og.png.
const esc = (t: string) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const answerMessage = (a: Answer, bot: string) => ({
  text: `<a href="${shareUrl(a)}">${esc(a.word + a.dot)}</a>`,
  parse_mode: "HTML",
  link_preview_options: { url: shareUrl(a), prefer_large_media: true },
  reply_markup: { inline_keyboard: [[sameButton(a, bot)]] },
});

function inlineResult(a: Answer, bot: string) {
  const m = answerMessage(a, bot);
  return {
    type: "article",
    id: a.slug,
    title: a.word + a.dot,
    description: a.tag,
    thumbnail_url: `${BASE}${a.slug}/thumb.jpg`,
    thumbnail_width: 320,
    thumbnail_height: 168,
    input_message_content: { message_text: m.text, parse_mode: m.parse_mode, link_preview_options: m.link_preview_options },
    reply_markup: m.reply_markup,
  };
}

// ---------- статистика ----------
let hmacKey: CryptoKey | null = null;
async function userHash(id?: number): Promise<string | null> {
  if (!id) return null;
  // Соль выведена из токена (SECRET). Сам id нигде не сохраняется.
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
  return `Отвечай одним словом — красиво.

В любом чате напиши @${name} и выбери ответ: «Да», «Нет», «У меня работает», «В пятницу не деплоим» и ещё ${n - 4}. В чат уйдёт ссылка с большой карточкой.

Или выбери группу ниже — пришлю ответ сюда, отправишь кому надо.`;
}
const tryButton = { text: "Попробовать в чате", switch_inline_query: "" };
// Главное меню: группы по две в ряд.
function groupsMenu(list: Answer[]) {
  const btns = GROUPS.map((g) => ({ text: `${g.title} · ${list.filter((a) => a.group === g.id).length}`, callback_data: "g:" + g.id }));
  const rows: unknown[][] = [[tryButton]];
  for (let i = 0; i < btns.length; i += 2) rows.push(btns.slice(i, i + 2));
  return { inline_keyboard: rows };
}
// Ответы одной группы + «назад».
function groupMenu(list: Answer[], groupId: string) {
  const items = list.filter((a) => a.group === groupId);
  const rows: unknown[][] = [];
  for (let i = 0; i < items.length; i += 2) {
    rows.push(items.slice(i, i + 2).map((a) => ({ text: a.word + a.dot, callback_data: "a:" + a.slug })));
  }
  rows.push([{ text: "← Все группы", callback_data: "back" }]);
  return { inline_keyboard: rows };
}

// ---------- обработка апдейтов ----------
// deno-lint-ignore no-explicit-any
async function handle(u: any): Promise<unknown | null> {
  const list = await getAnswers();
  const bot = await botName();

  if (u.inline_query) {
    const q: string = u.inline_query.query ?? "";
    later(log("inline_query", u.inline_query.from?.id, null, q));
    // Пустой запрос — топ-12, чтобы не вываливать весь список; по запросу — до 50 совпадений.
    const found = q.trim() ? search(list, q).slice(0, 50) : list.slice(0, 12);
    return {
      method: "answerInlineQuery",
      inline_query_id: u.inline_query.id,
      results: found.map((a) => inlineResult(a, bot)),
      cache_time: 60, // минута: правки ответов быстро доходят до всех
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
    later(tg("answerCallbackQuery", { callback_query_id: c.id }));
    if (!c.message) return null;
    const where = { chat_id: c.message.chat.id, message_id: c.message.message_id };
    const data: string = c.data ?? "";
    if (data.startsWith("g:") && GROUPS.some((g) => "g:" + g.id === data)) {
      return { method: "editMessageReplyMarkup", ...where, reply_markup: groupMenu(list, data.slice(2)) };
    }
    if (data === "back") return { method: "editMessageReplyMarkup", ...where, reply_markup: groupsMenu(list) };
    const a = list.find((x) => "a:" + x.slug === data);
    if (!a) return null;
    later(log("dm", c.from?.id, a.slug));
    return { method: "sendMessage", chat_id: c.message.chat.id, ...answerMessage(a, bot) };
  }

  const m = u.message;
  if (m && m.chat?.type === "private") {
    const isStart = typeof m.text === "string" && m.text.startsWith("/start");
    // Метка источника из ссылки t.me/<бот>?start=<метка>:
    //   a_<slug> — кнопка под карточкой в чате, w_<slug> — лендинг ответа, w_hub — главная сайта, r_<код> — ролик.
    // Для a_/w_ с ответом сразу открываем его группу. Метку пишем в query_text, ответ — в answer_slug.
    const payload: string = isStart ? (m.text.split(" ")[1] ?? "").slice(0, 64) : "";
    const from = /^[aw]_/.test(payload) ? list.find((a) => payload.slice(2) === a.slug) : undefined;
    if (isStart) later(log("start", m.from?.id, from?.slug ?? null, payload || undefined));
    return {
      method: "sendMessage",
      chat_id: m.chat.id,
      text: await helpText(list.length),
      reply_markup: from ? groupMenu(list, from.group) : groupsMenu(list),
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

// Ставим вебхук при каждом холодном старте — так он всегда совпадает с текущим токеном и URL.
async function ensureWebhook() {
  if (!TOKEN) return { ok: false, error: "BOT_TOKEN not set" };
  const webhook = await tg("setWebhook", {
    url: FN_URL,
    secret_token: SECRET,
    allowed_updates: ["message", "inline_query", "chosen_inline_result", "callback_query"],
  });
  await tg("setMyCommands", { commands: [{ command: "start", description: "Как пользоваться" }] });
  if (!webhook.ok) console.error("setWebhook failed", webhook);
  return webhook;
}
const ready = ensureWebhook().catch((e) => ({ ok: false, error: String(e) }));

async function status() {
  const webhook = await ready;
  const info = (await tg("getWebhookInfo", {})).result ?? {};
  const db = await fetch(`${SB_URL}/rest/v1/events?select=id&limit=1`, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
  return {
    bot: "@" + (await botName()),
    webhook_set: webhook.ok === true && info.url === FN_URL,
    pending: info.pending_update_count ?? null,
    last_error: info.last_error_message ?? null,
    db: db.ok ? "ok" : `error ${db.status}`,
    base: BASE,
    fallback_answers: (fallback as Answer[]).length,
    card_version: CARD_V,
  };
}

Deno.serve(async (req) => {
  if (!TOKEN) return new Response("BOT_TOKEN not set", { status: 500 });
  if (req.method === "GET") return Response.json(await status());

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
