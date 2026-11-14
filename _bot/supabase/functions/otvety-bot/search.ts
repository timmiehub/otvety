// Поиск ответа: по слову, синонимам «по смыслу», формам слова, с опечаткой в одну букву,
// плюс похожие ответы из той же группы. Без зависимостей — проверяется тестом search.test.ts.
export type Answer = {
  slug: string; word: string; dot: string; tag: string; keywords: string[]; top: number; group: string;
};

// Группы: порядок = порядок кнопок в личке. keywords — запросы, по которым показывается вся группа.
export const GROUPS = [
  { id: "agree", title: "✅ Согласие", keywords: ["согласие", "соглашаться", "одобрить", "положительно"] },
  { id: "maybe", title: "🤷 Ни да ни нет", keywords: ["ни да ни нет", "сомнение", "неуверенность", "не определился"] },
  { id: "refuse", title: "❌ Отказ", keywords: ["отказ", "отказать", "отрицательно"] },
  { id: "work", title: "💼 Работа", keywords: ["работа", "офис", "разработка", "айти", "it", "dev", "задача", "коллега", "менеджер", "проект"] },
  { id: "react", title: "😂 Реакции", keywords: ["реакция", "реакции", "эмоции", "смех", "мем"] },
  { id: "harsh", title: "🔥 Жёстко", keywords: ["мат", "жестко", "грубо", "18", "послать", "матом"] },
] as const;

export const norm = (s: string) =>
  s.toLowerCase().replace(/ё/g, "е").replace(/ъ/g, "ь").replace(/[^\p{L}\p{N}+ ]+/gu, " ").replace(/\s+/g, " ").trim();

// Грубая «основа» слова: для русского достаточно отрезать окончание (согласна → согла, согласен → согла).
const stem = (t: string) => (t.length >= 5 ? t.slice(0, Math.max(4, t.length - 2)) : t);

function lev1(a: string, b: string): boolean {
  if (Math.abs(a.length - b.length) > 1) return false;
  if (a.length === b.length) {
    const diff = [...a].map((c, i) => (c === b[i] ? -1 : i)).filter((i) => i >= 0);
    if (diff.length === 2 && diff[1] === diff[0] + 1 && a[diff[0]] === b[diff[1]] && a[diff[1]] === b[diff[0]]) return true;
  }
  let i = 0, j = 0, edits = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { i++; j++; continue; }
    if (++edits > 1) return false;
    if (a.length > b.length) i++;
    else if (b.length > a.length) j++;
    else { i++; j++; }
  }
  return edits + (a.length - i) + (b.length - j) <= 1;
}

// Насколько токен запроса совпадает со словом: 3 — начало слова, 2 — та же основа, 1 — опечатка.
function tokenMatch(q: string, w: string): number {
  if (w.startsWith(q)) return 3;
  if (q.length >= 5 && w.startsWith(stem(q))) return 2;
  if (q.length >= 5 && (lev1(q, w) || lev1(q, w.slice(0, q.length)) || lev1(q, w.slice(0, q.length + 1)))) return 1;
  return 0;
}

// Все ли слова запроса нашлись среди слов текста; возвращает худшее совпадение (0 — нет).
function allTokens(qTokens: string[], words: string[]): number {
  let worst = 3;
  for (const t of qTokens) {
    let best = 0;
    for (const w of words) best = Math.max(best, tokenMatch(t, w));
    if (!best) return 0;
    worst = Math.min(worst, best);
  }
  return worst;
}

function score(a: Answer, q: string, qTokens: string[]): number {
  const w = norm(a.word);
  const kws = [...a.keywords, a.slug.replace(/-/g, " ")].map(norm);
  if (w === q) return 100;
  if (kws.includes(q)) return 70;
  const words = [w, ...kws].join(" ").split(" ");
  if (q.length <= 2) return words.includes(q) ? 45 : 0; // «да», «ок»: только целым словом
  if (w.startsWith(q)) return 80;
  if (kws.some((k) => k.startsWith(q))) return 60;
  const m = allTokens(qTokens, words);
  return m === 3 ? 38 : m === 2 ? 34 : m === 1 ? 25 : 0;
}

function groupScore(groupId: string, q: string, qTokens: string[]): number {
  const g = GROUPS.find((x) => x.id === groupId);
  if (!g) return 0;
  const words = g.keywords.map(norm); // название группы («Ни да ни нет») в поиске не участвует
  if (words.includes(q)) return 65; // запрос = ключ группы: вся группа сразу после точных совпадений
  return q.length >= 3 && allTokens(qTokens, words.join(" ").split(" ")) >= 2 ? 20 : 0;
}

export function search(list: Answer[], raw: string): Answer[] {
  const q = norm(raw);
  if (!q) return list;
  const qTokens = q.split(" ");
  const scores = new Map<string, number>();
  for (const a of list) scores.set(a.slug, Math.max(score(a, q, qTokens), groupScore(a.group, q, qTokens)));
  // «Похожие по смыслу»: к уверенным совпадениям добавляем соседей по группе, ниже их.
  const strongGroups = new Set(list.filter((a) => scores.get(a.slug)! >= 34).map((a) => a.group));
  for (const a of list) {
    if (strongGroups.has(a.group) && scores.get(a.slug)! < 30) scores.set(a.slug, 30);
  }
  return list
    .filter((a) => scores.get(a.slug)! > 0)
    .sort((x, y) => scores.get(y.slug)! - scores.get(x.slug)! || x.top - y.top);
}
