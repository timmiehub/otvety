// Поиск ответа по слову и синонимам. Без зависимостей — проверяется тестом search.test.ts.
export type Answer = { slug: string; word: string; dot: string; tag: string; keywords: string[]; top: number };

export const norm = (s: string) =>
  s.toLowerCase().replace(/ё/g, "е").replace(/ъ/g, "ь").replace(/[^\p{L}\p{N}+ ]+/gu, " ").replace(/\s+/g, " ").trim();

function score(a: Answer, q: string): number {
  const w = norm(a.word);
  const kws = [...a.keywords, a.slug.replace(/-/g, " ")].map(norm);
  if (w === q) return 100;
  if (w.startsWith(q)) return 80;
  if (kws.includes(q)) return 70;
  if (kws.some((k) => k.startsWith(q))) return 60;
  if (w.includes(q)) return 50;
  if (kws.some((k) => k.includes(q))) return 40;
  // все слова запроса нашлись как начала слов ответа/синонимов
  const words = [w, ...kws].join(" ").split(" ");
  if (q.split(" ").every((t) => words.some((x) => x.startsWith(t)))) return 30;
  return 0;
}

export function search(list: Answer[], raw: string): Answer[] {
  const q = norm(raw);
  if (!q) return list;
  return list
    .map((a) => ({ a, s: score(a, q) }))
    .filter((x) => x.s > 0)
    .sort((x, y) => y.s - x.s || x.a.top - y.a.top)
    .map((x) => x.a);
}

