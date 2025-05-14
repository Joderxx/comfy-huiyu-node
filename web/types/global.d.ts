import {ComfyApp} from "@comfyorg/comfyui-frontend-types"
import {LGraph} from "@comfyorg/litegraph";

export declare global {
  interface Window {
    app: ComfyApp
    graph: LGraph;
    comfyAPI: {
      utils: {
        downloadBlob(file: string, blob: Blob): void
      }
    }
  }
  const app: ComfyApp
}