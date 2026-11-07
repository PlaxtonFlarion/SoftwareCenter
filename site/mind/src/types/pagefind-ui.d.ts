declare module '@pagefind/default-ui' {
  /** 页面持有搜索界面实例，移除页面时销毁其 DOM 和订阅。 */
  export class PagefindUI {
    constructor(options: {
      element: HTMLElement;
      bundlePath: string;
      baseUrl: string;
      showImages: boolean;
      showSubResults: boolean;
      translations: Record<string, string>;
    });
    destroy(): void;
  }
}
