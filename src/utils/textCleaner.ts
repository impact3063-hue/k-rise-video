/**
 * 🎯 Text Cleaner Utility - 句読点完全除去システム
 * 
 * すべての句読点・約物を検出し、空文字に置換する最強の正規表現フィルター
 * 
 * 対象記号（Unicode完全網羅）:
 * - 句点系: 。 (U+3002), . (半角), ． (全角U+FF0E)
 * - 読点系: 、 (U+3001), , (半角), ， (全角U+FF0C)
 * - 中黒系: ・ (U+30FB), ･ (半角U+FF65)
 * - その他: ！ ？ ! ? … ‥ 「 」 『 』 （ ） ( ) など
 */

/**
 * 🎯 句読点および文章記号を完全に検出する正規表現
 * 
 * Unicode範囲:
 * - \u3000-\u303F: CJK記号及び句読点
 * - \uFF00-\uFFEF: 半角・全角形
 * - 個別指定: 頻出する句読点を明示的に列挙
 */
export const PUNCTUATION_REGEX = /[、，,。．.・･！？!?…‥「」『』（）()【】［］\[\]〈〉《》〔〕｛｝\{\}〜～\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]/g;

/**
 * より厳密な句読点のみの正規表現（保守的なアプローチ）
 * 
 * 対象:
 * - 句点: 。 . ．
 * - 読点: 、 , ，
 * - 中黒: ・ ･
 */
export const STRICT_PUNCTUATION_REGEX = /[、，,。．.・･\u3001\u3002\uFF0C\uFF0E\u30FB\uFF65]/g;

/**
 * テキストから句読点を完全に除去する関数
 * 
 * @param text - クリーニング対象のテキスト
 * @param strict - true: 厳密モード（句読点・中黒のみ）, false: 広範囲モード（すべての記号）
 * @returns クリーニング済みテキスト
 * 
 * @example
 * cleanText("成功したいなら、") // => "成功したいなら"
 * cleanText("応募はLINEから。") // => "応募はLINEから"
 * cleanText("この瞬間。") // => "この瞬間"
 * cleanText("まさかの直接審査！？") // => "まさかの直接審査" (strict=false)
 * cleanText("まさかの直接審査！？", true) // => "まさかの直接審査！？" (strict=true)
 */
export const cleanText = (text: string, strict: boolean = true): string => {
  if (!text) return "";
  
  const regex = strict ? STRICT_PUNCTUATION_REGEX : PUNCTUATION_REGEX;
  return text.replace(regex, "");
};

/**
 * 文字が句読点かどうかを判定する関数
 * 
 * @param char - 判定対象の文字（1文字）
 * @param strict - true: 厳密モード, false: 広範囲モード
 * @returns 句読点の場合true
 */
export const isPunctuation = (char: string, strict: boolean = true): boolean => {
  if (!char || char.length === 0) return false;
  
  const regex = strict ? STRICT_PUNCTUATION_REGEX : PUNCTUATION_REGEX;
  return regex.test(char);
};

/**
 * テキストから句読点を除去し、空文字になった場合はnullを返す
 * 
 * @param text - クリーニング対象のテキスト
 * @param strict - true: 厳密モード, false: 広範囲モード
 * @returns クリーニング済みテキスト、または空の場合null
 */
export const cleanTextOrNull = (text: string, strict: boolean = true): string | null => {
  const cleaned = cleanText(text, strict);
  return cleaned.trim() === "" ? null : cleaned;
};

/**
 * デバッグ用: テキスト内の句読点を検出してリスト化
 * 
 * @param text - 検査対象のテキスト
 * @returns 検出された句読点の配列
 */
export const detectPunctuation = (text: string): string[] => {
  if (!text) return [];
  
  const matches = text.match(PUNCTUATION_REGEX);
  return matches ? Array.from(new Set(matches)) : [];
};

/**
 * デバッグ用: テキスト内の句読点を視覚的にハイライト
 * 
 * @param text - 検査対象のテキスト
 * @returns 句読点を[記号]形式でハイライトしたテキスト
 */
export const highlightPunctuation = (text: string): string => {
  if (!text) return "";
  
  return text.replace(PUNCTUATION_REGEX, (match) => `[${match}]`);
};
