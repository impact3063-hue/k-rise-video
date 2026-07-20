/**
 * 🎯 Word-Aware Line Breaking Utility
 * BudouXを使用した日本語の自然な改行処理
 * 
 * 機能:
 * - 単語の途中で改行しない（「プロデューサー」を「プロデューサ / ー」と分割しない）
 * - 1文字だけの孤立改行を防止
 * - 文脈を考慮した自然な改行位置の決定
 */

import { loadDefaultJapaneseParser } from 'budoux';

// BudouXパーサーの初期化（シングルトン）
let parser: ReturnType<typeof loadDefaultJapaneseParser> | null = null;

function getParser() {
  if (!parser) {
    parser = loadDefaultJapaneseParser();
  }
  return parser;
}

/**
 * 文字列を自然な単位（単語・フレーズ）に分割
 * @param text 分割する文字列
 * @returns 分割された文字列の配列
 */
export function splitIntoWords(text: string): string[] {
  const budouxParser = getParser();
  return budouxParser.parse(text);
}

/**
 * 文字データを単語単位でグループ化
 * @param characters 文字データの配列
 * @param text 元のテキスト
 * @returns 単語ごとにグループ化された文字データ
 */
export function groupCharactersByWords<T extends { char: string }>(
  characters: T[],
  text: string
): T[][] {
  // BudouXで単語分割
  const words = splitIntoWords(text);
  
  const groups: T[][] = [];
  let charIndex = 0;
  
  for (const word of words) {
    const wordChars: T[] = [];
    const wordLength = word.length;
    
    for (let i = 0; i < wordLength && charIndex < characters.length; i++) {
      wordChars.push(characters[charIndex]);
      charIndex++;
    }
    
    if (wordChars.length > 0) {
      groups.push(wordChars);
    }
  }
  
  return groups;
}

/**
 * 単語グループを行に分割（最大文字数を考慮）
 * @param wordGroups 単語ごとにグループ化された文字データ
 * @param maxCharsPerLine 1行あたりの最大文字数（目安）
 * @returns 行ごとに分割された単語グループ
 */
export function splitIntoLines<T>(
  wordGroups: T[][],
  maxCharsPerLine: number = 20
): T[][][] {
  const lines: T[][][] = [];
  let currentLine: T[][] = [];
  let currentLineLength = 0;
  
  for (const wordGroup of wordGroups) {
    const wordLength = wordGroup.length;
    
    // 現在の行に追加すると最大文字数を超える場合
    if (currentLineLength > 0 && currentLineLength + wordLength > maxCharsPerLine) {
      // 現在の行を確定して新しい行を開始
      lines.push(currentLine);
      currentLine = [wordGroup];
      currentLineLength = wordLength;
    } else {
      // 現在の行に追加
      currentLine.push(wordGroup);
      currentLineLength += wordLength;
    }
  }
  
  // 最後の行を追加
  if (currentLine.length > 0) {
    lines.push(currentLine);
  }
  
  return lines;
}

/**
 * 文字数に基づいて最適な1行あたりの文字数を計算
 * @param totalChars 総文字数
 * @returns 推奨される1行あたりの文字数
 */
export function calculateOptimalLineLength(totalChars: number): number {
  if (totalChars <= 15) return totalChars; // 短い場合は1行
  if (totalChars <= 30) return Math.ceil(totalChars / 2); // 2行に分割
  return Math.ceil(totalChars / 3); // 3行に分割
}
