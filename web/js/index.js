import { app } from "../../scripts/app.js";
const prefixName = "";
const varPrefixName = "ComfyMasterVar_";
async function checkVarName() {
  const p = await window.app.graphToPrompt();
  for (const node of p.workflow.nodes) {
    const name = node.type;
    if (name === `${prefixName}CTool_ImageWorkflowMetadataTestNode`) {
      alert("存在节点 ‘图片元数据(测试)’");
      return false;
    }
    if (name === `${prefixName}CTool_ImageMaskTestNode`) {
      alert("存在节点 ‘遮罩数据(测试)’");
      return false;
    }
  }
  let findOutput = false;
  for (let node of Object.values(p.output)) {
    if (!node["class_type"].startsWith(`${prefixName}CMaster_Output`) && !node["class_type"].startsWith(`${prefixName}CMaster_Input`)) {
      continue;
    }
    if (node["class_type"].startsWith(`${prefixName}CMaster_Output`)) {
      findOutput = true;
    }
    const varName = node.inputs["var_name"];
    if (!varName || typeof varName !== "string" || varName.trim() === "") {
      alert(`${node["class_type"]} 没有变量名`);
      return false;
    }
  }
  if (!findOutput) {
    alert("没有找到：输出节点");
    return false;
  }
  return true;
}
function getGroup(id, workflow, outputs) {
  const node = workflow.nodes.find((e) => e.id === parseInt(id));
  if (!node) {
    return [];
  }
  const ret = [];
  if (node.type === `${prefixName}CMaster_InputSwitchNode` || node.type === `${prefixName}CMaster_InputSwitchGroupNode`) {
    const n = outputs[id]["inputs"]["open_data"];
    if (n) {
      ret.push(`single-${n[0]}`);
    }
  }
  for (let group of workflow.groups) {
    const [posX, posY] = node.pos;
    const [x, y, width, height] = group.bounding;
    if (posX >= x && posX <= x + width && posY >= y && posY <= y + height) {
      ret.push(`group-${group.title}`);
    }
  }
  ret.push(`single-${id}`);
  return ret;
}
async function exportPrompt() {
  const p = await window.app.graphToPrompt();
  const workflow = { ...p.output };
  let metadataNode;
  let metadataNodeKey;
  for (let [key, value] of Object.entries(workflow)) {
    if (value.class_type === `${prefixName}CMaster_InputImage` || value["class_type"] === `${prefixName}CMaster_InputMaskImageNode`) {
      value.inputs["image"] = "";
    } else if (value.class_type === `${prefixName}LoadImageToBase64`) {
      delete workflow[key];
    } else if (value.class_type === `${prefixName}WorkflowMetadataConfig`) {
      metadataNode = value;
      metadataNodeKey = key;
    }
    if (value._meta) {
      value._meta.group = getGroup(key, p.workflow, p.output);
    }
  }
  if (metadataNodeKey) {
    delete workflow[metadataNodeKey];
  }
  let modelType = ["其他", "SD1.5", "SDXL", "FLUX"].indexOf(metadataNode?.inputs?.modelType || "");
  if (modelType === -1) {
    modelType = 0;
  }
  let type = ["默认", "局部重绘", "放大", "局部修复"].indexOf(metadataNode?.inputs?.type || "");
  if (type === -1) {
    type = 0;
  }
  const saveObj = {
    code: metadataNode?.inputs?.code || "",
    name: metadataNode?.inputs?.name || "",
    description: metadataNode?.inputs?.description || "",
    type,
    modelType,
    groupInfo: metadataNode?.inputs?.groupInfo || "",
    maxWidth: metadataNode?.inputs?.maxWidth || 2048,
    maxHeight: metadataNode?.inputs?.maxHeight || 2048,
    workflow,
    params: Object.values(workflow).filter((e) => e.class_type.startsWith(`${prefixName}CMaster_Input`)).map((e) => parseInput(e)),
    outputs: Object.values(workflow).filter((e) => e.class_type.startsWith(`${prefixName}CMaster_Output`)).map((e) => parseOutput(e))
  };
  return {
    name: metadataNode?.inputs?.name || "",
    data: JSON.stringify(saveObj, null, 2)
  };
}
const ParameterType = {
  Boolean: 1,
  Number: 2,
  String: 3,
  Image: 4,
  Range_Number: 5,
  Enum_String: 6,
  Float: 7,
  Range_Float: 8,
  Image_Mask: 9,
  Switch: 10,
  Switch_Group: 11,
  Enum_Int: 12,
  Enum_Float: 13
};
const algorithms = ["", "固定值", "随机值", "递增", "递减"];
function parseInput(node) {
  const type = node.class_type;
  const varName = node.inputs["var_name"];
  const newVarName = `${varPrefixName}${varName}`;
  const description = node.inputs["description"] || varName;
  const isExport = node.inputs["export"];
  const order = node.inputs["order"];
  const placeholder = node.inputs["placeholder"] || "";
  const group = (node["_meta"] || {})["group"] || [];
  const defaultGenerateAlgorithm = Math.max(0, algorithms.indexOf(node.inputs["default_generate_algorithm"]));
  let ret = {
    key: newVarName,
    name: description,
    type: ParameterType.Image,
    isExport,
    order: order || 0,
    defaultGenerateAlgorithm,
    group,
    placeholder
  };
  if (type === `${prefixName}CMaster_InputImage`) {
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Image,
      isExport,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputString`) {
    const text = node.inputs["text"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.String,
      isExport,
      stringDefaultValue: text,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputEnumString`) {
    const text = node.inputs["text"];
    const enums = node.inputs["enums"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_String,
      isExport,
      stringDefaultValue: text,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputBoolean`) {
    const num = node.inputs["value"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Boolean,
      isExport,
      boolDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputInt`) {
    const num = node.inputs["number"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Number,
      isExport,
      numberDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputRangeInt`) {
    const num = node.inputs["number"];
    const min = node.inputs["min"];
    const max = node.inputs["max"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Range_Number,
      isExport,
      numberDefaultValue: num,
      minNumberValue: min,
      maxNumberValue: max,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputEnumInt`) {
    const num = node.inputs["number"];
    const enums = node.inputs["enums"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_Int,
      isExport,
      numberDefaultValue: num,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputFloat`) {
    const num = node.inputs["number"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Float,
      isExport,
      floatDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputRangeFloat`) {
    const num = node.inputs["number"];
    const min = node.inputs["min"];
    const max = node.inputs["max"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Range_Float,
      isExport,
      floatDefaultValue: num,
      minFloatValue: min,
      maxFloatValue: max,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputEnumFloat`) {
    const num = node.inputs["number"];
    const enums = node.inputs["enums"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_Float,
      isExport,
      numberDefaultValue: num,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputCheckpoint`) {
    const text = node.inputs["ckpt_name"];
    const enums = node.inputs["checkpoints"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_String,
      isExport,
      stringDefaultValue: text,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputLoraNode`) {
    const text = node.inputs["lora_name"];
    const enums = node.inputs["loras"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Enum_String,
      isExport,
      stringDefaultValue: text,
      enumStringValue: enums,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputMaskImageNode`) {
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Image_Mask,
      isExport,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputSwitchNode`) {
    const num = node.inputs["value"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Switch,
      isExport,
      boolDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  } else if (type === `${prefixName}CMaster_InputSwitchGroupNode`) {
    const num = node.inputs["value"];
    ret = {
      key: newVarName,
      name: description,
      type: ParameterType.Switch_Group,
      isExport,
      boolDefaultValue: num,
      order: order || 0,
      defaultGenerateAlgorithm,
      group,
      placeholder
    };
  }
  return ret;
}
const OutputType = {
  None: 0,
  Image: 2
};
function parseOutput(node) {
  const type = node.class_type;
  const varName = node.inputs["var_name"];
  const newVarName = `${varPrefixName}${varName}`;
  const description = node.inputs["description"] || varName;
  const isExport = node.inputs["export"];
  const order = node.inputs["order"];
  let ret = {
    key: newVarName,
    name: description,
    type: OutputType.None,
    isExport,
    order: order || 0
  };
  if (type === `${prefixName}CMaster_OutputImage`) {
    ret.type = OutputType.Image;
  }
  return ret;
}
async function getFilename(defaultName) {
  if (await window.app.api.getSetting("Comfy.PromptFilename")) {
    defaultName = prompt("保存为:", defaultName);
    if (!defaultName) return;
    if (!defaultName.toLowerCase().endsWith(".json")) {
      defaultName += ".json";
    }
  }
  return defaultName;
}
async function exportJson(name, json) {
  const blob = new Blob([json], { type: "application/json" });
  const file = await getFilename(`${name}.json`);
  if (!file) return;
  window.comfyAPI.utils.downloadBlob(file, blob);
}
async function copy(text) {
  let clipboard = navigator.clipboard || {
    writeText: (str) => {
      return new Promise((resolve) => {
        let copyInput = document.createElement("input");
        copyInput.value = str;
        document.body.appendChild(copyInput);
        copyInput.select();
        document.execCommand("copy");
        document.body.removeChild(copyInput);
        resolve();
      });
    }
  };
  if (clipboard) {
    await clipboard.writeText(text);
  }
}
const extension = {
  name: "ComfyMaster",
  commands: [
    {
      id: "copy-profile",
      label: "复制配置",
      function: async () => {
        if (!await checkVarName()) {
          return;
        }
        const resp = await exportPrompt();
        await copy(resp.data);
        alert("配置复制到剪切板成功");
      }
    },
    {
      id: "export-profile",
      label: "导出配置",
      function: async () => {
        if (!await checkVarName()) {
          return;
        }
        const resp = await exportPrompt();
        await exportJson(resp.name, resp.data);
      }
    }
  ],
  menuCommands: [
    {
      path: ["绘屿AI"],
      commands: ["copy-profile"]
    },
    {
      path: ["绘屿AI"],
      commands: ["export-profile"]
    }
  ]
};
app.registerExtension(extension);
//# sourceMappingURL=index.js.map
