// node search.test.ts  (Node 22.18+/24 — понимает TypeScript)
import { search, GROUPS, type Answer } from "./search.ts";
import { readFileSync } from "node:fs";
const list: Answer[] = JSON.parse(readFileSync(new URL("./answers.json", import.meta.url), "utf8")).sort((a: Answer, b: Answer) => a.top - b.top);
const top = (q: string, n = 4) => search(list, q).slice(0, n).map((a) => a.slug);

// [запрос, что должно быть в первых 4]
const cases: [string, string][] = [
  ["", "da"], ["да", "da"], ["нет", "net"], ["отказ", "net"], ["ОТКАЗ", "net"], ["хз", "ne-znayu"],
  ["пятница", "v-pyatnicu-ne-deploim"], ["деплой", "v-pyatnicu-ne-deploim"], ["баг", "ne-bag-a-ficha"],
  ["у меня", "u-menya-rabotaet"], ["кеш", "u-menya-rabotaet"], ["созвон", "sozvonimsya"], ["zoom", "sozvonimsya"],
  ["молодец", "krasava"], ["потом", "pozzhe"], ["отъебись", "otebis"], ["отьебись", "otebis"], ["зона", "ne-moya-zona"],
  ["пофиг", "pohuy"], ["ok", "ok"], ["ладн", "ladno"], ["письм", "prishli-pismenno"], ["не согл", "ne-soglasovano"],
  // по смыслу и формам слова
  ["согласна", "da"], ["согласовали", "soglasovano"], ["занят", "pozzhe"], ["некогда", "pozzhe"], ["огонь", "krasava"],
  ["умница", "krasava"], ["бред", "huynya"], ["без разницы", "pohuy"], ["надоел", "otstan"], ["глюк", "ne-bag-a-ficha"],
  ["релизим", "v-pyatnicu-ne-deploim"], ["позвони", "sozvonimsya"], ["аврал", "srochno"], ["не уверен", "ne-znayu"],
  // опечатки
  ["молодеца", "krasava"], ["созвно", "sozvonimsya"], ["пятнциа", "v-pyatnicu-ne-deploim"],
  // новые ответы
  ["спс", "spasibo"], ["благодарю", "spasibo"], ["понятно", "yasno"], ["сейчас", "scha"], ["щас", "scha"], ["ахаха", "oru"],
  ["лол", "oru"], ["стыдно", "kring"], ["извини", "sorian"], ["сорри", "sorian"], ["факт", "baza"], ["так себе", "nu-takoe"],
  ["спокойной ночи", "ya-splyu"], ["сделано", "gotovo"], ["done", "gotovo"], ["принял", "vzyal-v-rabotu"], ["посмотрю", "glyanu"],
  ["отпуск", "ya-v-otpuske"], ["понедельник", "napomni"], ["пинг", "au"], ["ты где", "au"], ["еду", "uzhe-vyhozhu"],
  ["опаздываю", "uzhe-vyhozhu"], ["не могу говорить", "perezvonyu"], ["не сегодня", "ne-segodnya"], ["нормально", "norm"],
  ["как хочешь", "kak-skazhesh"], ["легко", "bez-problem"], ["без созвона", "a-mozhno-v-chat"], ["на встрече", "na-sozvone"],
  // приветствия и «забей»
  ["привет", "privet"], ["здарова", "privet"], ["хай", "privet"], ["добрый день", "privet"], ["доброе утро", "dobroe-utro"],
  ["утро", "dobroe-utro"], ["забей", "pohuy"], ["забудь", "pohuy"], ["забец", "pohuy"],
  // группы
  ["реакции", "oru"],
  ["работа", "u-menya-rabotaet"], ["мат", "otstan"], ["жестко", "otstan"],
];
let fail = 0;
for (const [q, want] of cases) {
  const got = top(q);
  const ok = got.includes(want);
  if (!ok) fail++;
  console.log(ok ? "ok  " : "FAIL", JSON.stringify(q).padEnd(16), got.join(", "));
}
// похожие: на «да» после «Да» идут остальные из группы согласия
const sim = search(list, "да").map((a) => a.slug);
const agree = list.filter((a) => a.group === "agree").map((a) => a.slug);
const simOk = agree.every((s) => sim.includes(s));
console.log(simOk ? "ok  " : "FAIL", "«да» тянет всю группу согласия:", sim.join(", "));
if (!simOk) fail++;
const workSlugs = list.filter((a) => a.group === "work").map((a) => a.slug);
const work = search(list, "работа").slice(0, workSlugs.length).map((a) => a.slug).sort().join();
const workOk = work === workSlugs.sort().join();
console.log(workOk ? "ok  " : "FAIL", "«работа»: первой идёт вся группа работы");
const short = search(list, "да").length;
console.log(short <= 10 ? "ok  " : "FAIL", "«да» не тянет лишнего:", short, "результатов");
if (short > 10) fail++;
if (!workOk) fail++;
console.log(GROUPS.length, "групп;", fail ? `${fail} провалов` : "всё ок");
if (fail) process.exit(1);
