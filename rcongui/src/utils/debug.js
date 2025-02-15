const debug = (name) => (...args) => {
  if (process.env.DEBUG) {
    console.log(`[${name}]`, ...args);
  }
};

export default debug;