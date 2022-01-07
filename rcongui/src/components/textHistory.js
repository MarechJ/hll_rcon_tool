import _ from "lodash";

const PREFIX = "autocomplete_";

const getAllNamespaces = () => {
  let namespaces = ["punitions", "welcome", "broadcast", "watchlist"];

  return namespaces.filter((v) => {
    if (!v || v.includes("undefined")) {
      return false;
    }
    const texts = new TextHistory(v).getTexts();

    if (texts.length === 0) {
      return false;
    }
    return true;
  });
};


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

  deleteTextByIdx(index) {
    const texts = this.getTexts();
    texts.splice(index, 1);
    localStorage.setItem(this.namespace, JSON.stringify(texts));
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
export { TextHistory, getAllNamespaces };
