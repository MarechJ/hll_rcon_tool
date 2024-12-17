const PREFIX = "autocomplete_";

class TextHistory {
  constructor(namespace) {
    this.namespace = PREFIX + namespace;
  }

  getTexts() {
    let texts = localStorage.getItem(this.namespace);

    if (!texts) {
      texts = [];
      localStorage.setItem(this.namespace, JSON.stringify(texts));
    } else {
      texts = JSON.parse(texts);
    }

    texts.sort((a, b) => a.toLowerCase() > b.toLowerCase());

    return texts;
  }

  saveText(text, sharedMessages = []) {
    if (!text || sharedMessages.includes(text)) {
      return;
    }
    const texts = this.getTexts();
    texts.push(text);
    localStorage.setItem(this.namespace, JSON.stringify(_.uniq(texts)));
  }

  clear() {
    localStorage.removeItem(this.namespace);
  }
}

export default TextHistory;
export { TextHistory };
