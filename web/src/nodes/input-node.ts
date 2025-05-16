import {LGraphNode} from "@comfyorg/litegraph";
import {ComfyApp} from "@comfyorg/comfyui-frontend-types";

export function changeInputForInputNode(node: LGraphNode, app: ComfyApp) {
  node.onConnectInput= function () {
    app.extensionManager.toast.add({
          severity: 'warn',
          summary: '警告',
          detail: '节点输入应避免连接其他节点',
          life: 3000
        })
    return  true;
  }
}