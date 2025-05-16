import {LGraphNode} from "@comfyorg/litegraph";
import {ComfyApp} from "@comfyorg/comfyui-frontend-types";
import {prefixName} from "@/common";
import {changeInputForInputNode} from "@/nodes/input-node";

export function nodeCreated(node: LGraphNode, app: ComfyApp) {
    node.onNodeCreated = function () {
      if (node.type.startsWith(`${prefixName}CMaster_Input`)) {
        changeInputForInputNode(node, app)
      }
    }
}