import type { Element, Root } from 'hast';
import { toString } from 'hast-util-to-string';
import { visit } from 'unist-util-visit';

/** 保留旧站的 ASCII 章节书签，同时使用新渲染器的中文锚点。 */
export default function legacyAnchors() {
  return (tree: Root) => {
    const used = new Set<string>();
    const currentIds = new Set<string>();
    visit(tree, 'element', (node) => {
      if (typeof node.properties.id === 'string') currentIds.add(node.properties.id);
    });
    let titleRemoved = false;
    visit(tree, 'element', (node) => {
      if (!/^h[1-6]$/.test(node.tagName)) return;
      const title = toString(node).replace(/\s+[（(][^()（）]+[)）]\s*$/, '');
      const base = title.normalize('NFKD').replace(/[^\x00-\x7F]/g, '').toLowerCase()
        .replace(/[^\w\s-]/g, '').trim().replace(/[-\s]+/g, '-');
      let id = base;
      let suffix = 0;
      while (!id || used.has(id)) id = `${base}_${++suffix}`;
      used.add(id);
      if (node.tagName === 'h1' && !titleRemoved) {
        // 页面标题由 Starlight 渲染；正文首个标题仅保留旧书签位置。
        titleRemoved = true;
        node.tagName = 'span';
        node.properties = { id, className: ['legacy-anchor'], ariaHidden: 'true' };
        node.children = [];
      } else if (id !== node.properties.id && !currentIds.has(id)) {
        const anchor: Element = {
          type: 'element', tagName: 'span',
          properties: { id, className: ['legacy-anchor'], ariaHidden: 'true' }, children: [],
        };
        node.children.unshift(anchor);
      }
    });
  };
}
