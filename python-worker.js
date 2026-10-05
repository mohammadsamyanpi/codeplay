let runtime;
self.onmessage = async ({ data }) => {
  try {
    if (!runtime) {
      importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.2/full/pyodide.js');
      runtime = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.29.2/full/' });
    }
    const output = [];
    runtime.setStdout({ batched: text => output.push(text) });
    runtime.setStderr({ batched: text => output.push(text) });
    const scope = runtime.toPy({});
    try {
      await runtime.runPythonAsync(data.code, { globals: scope });
      const name = scope.has('name') ? scope.get('name') : null;
      const checks = [typeof name === 'string' && name.length > 0, output.some(line => line.trim() === 'Hello, CodePlay!'), output.length > 0];
      self.postMessage({ output: output.join('\n'), checks });
    } finally {
      scope.destroy();
    }
  } catch (error) {
    self.postMessage({ error: String(error.message || error) });
  }
};
