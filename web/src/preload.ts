import {checkVarName, exportPrompt, exportJson} from "./enhanced-btn"
import {ComfyApp, ComfyExtension} from "@comfyorg/comfyui-frontend-types";
import {LGraphNode} from "@comfyorg/litegraph";
import {nodeCreated} from "./nodes/core";

const extension: ComfyExtension = {
  name: "HuiYuAIExtension",
  nodeCreated(node: LGraphNode, app: ComfyApp) {
    nodeCreated(node, app)
  },
  commands: [
    {
      id: "export-profile",
      label: "导出配置",
      function: async () => {
        if (!await checkVarName()) {
          return
        }
        const resp = await exportPrompt()
        await exportJson(resp.name, resp.data)
      }
    }
  ],
  menuCommands: [
    {
      path: ['绘屿AI'],
      commands: ['export-profile']
    }
  ]
}

app.registerExtension(extension)

