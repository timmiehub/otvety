// node search.test.ts  (Node 22.18+/24 — понимает TypeScript)
import { search, type Answer } from "./search.ts";
import { readFileSync } from "node:fs";
const list: Answer[] = JSON.parse(readFileSync(new URL("./answers.json", import.meta.url), "utf8")).sort((a: Answer, b: Answer) => a.top - b.top);
const top = (q: string) => search(list, q).slice(0, 4).map((a) => a.slug);
const cases: [string, string][] = [
  ["", "da"], ["да", "da"], ["нет", "net"], ["отказ", "net"], ["ОТКАЗ", "net"], ["хз", "ne-znayu"],
  ["пятница", "v-pyatnicu-ne-deploim"], ["деплой", "v-pyatnicu-ne-deploim"], ["баг", "ne-bag-a-ficha"],
  ["у меня", "u-menya-rabotaet"], ["кеш", "u-menya-rabotaet"], ["созвон", "sozvonimsya"], ["zoom", "sozvonimsya"],
  ["молодец", "krasava"], ["потом", "pozzhe"], ["отъебись", "otebis"], ["отьебись", "otebis"], ["зона", "ne-moya-zona"],
  ["пофиг", "pohuy"], ["ok", "ok"], ["ладн", "ladno"], ["письм", "prishli-pismenno"], ["не согл", "ne-soglasovano"],
];
let fail = 0;
for (const [q, want] of cases) {
  const got = top(q);
  const ok = got.includes(want);
  if (!ok) fail++;
  console.log(ok ? "ok  " : "FAIL", JSON.stringify(q).padEnd(14), got.join(", "));
}
console.log("отказ →", top("отказ").join(", "));
if (fail) process.exit(1);
