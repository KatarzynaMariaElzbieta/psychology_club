var dmcfuncs = window.dashMantineFunctions = window.dashMantineFunctions || {};

function getEditorFromPayload(payload) {
  if (payload && payload.editor) {
    return payload.editor;
  }
  return null;
}

function runCommand(editor, commandName) {
  if (!editor || !editor.chain) {
    return;
  }
  var chain = editor.chain().focus();
  if (typeof chain[commandName] !== "function") {
    return;
  }
  chain[commandName]().run();
}

dmcfuncs.rteInsertTable = function (payload, options) {
  var editor = getEditorFromPayload(payload);
  if (!editor || !editor.chain) {
    return;
  }
  var tableOptions = options && options.table ? options.table : { rows: 3, cols: 3, withHeaderRow: true };
  editor.chain().focus().insertTable(tableOptions).run();
};

dmcfuncs.rteAddRowBefore = function (payload) {
  runCommand(getEditorFromPayload(payload), "addRowBefore");
};

dmcfuncs.rteAddRowAfter = function (payload) {
  runCommand(getEditorFromPayload(payload), "addRowAfter");
};

dmcfuncs.rteDeleteRow = function (payload) {
  runCommand(getEditorFromPayload(payload), "deleteRow");
};

dmcfuncs.rteAddColumnBefore = function (payload) {
  runCommand(getEditorFromPayload(payload), "addColumnBefore");
};

dmcfuncs.rteAddColumnAfter = function (payload) {
  runCommand(getEditorFromPayload(payload), "addColumnAfter");
};

dmcfuncs.rteDeleteColumn = function (payload) {
  runCommand(getEditorFromPayload(payload), "deleteColumn");
};

dmcfuncs.rteDeleteTable = function (payload) {
  runCommand(getEditorFromPayload(payload), "deleteTable");
};
