class ProgrammingError extends Error {
  constructor(message) {
    super(message);
    this.name = "ProgrammingError";
  }
}

export default ProgrammingError;
