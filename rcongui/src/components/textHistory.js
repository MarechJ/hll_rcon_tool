import _ from 'lodash'
import { startsWith } from 'lodash/string'


const PREFIX = "autocomplete_"

const getAllNamespaces = () => (
    Object.keys(localStorage).filter(e => startsWith(e, PREFIX))
)

class TextHistory {
    constructor(namespace) {
        this.namespace = PREFIX + namespace
    }

    getTexts() {
        let texts = localStorage.getItem(this.namespace)
        console.log("Loading history for ", this.namespace)
        if (!texts) {
            console.log("Loading history for ", this.namespace)
            texts = []
            localStorage.setItem(this.namespace, JSON.stringify(texts))
        } else {
            texts = JSON.parse(texts)
        }
        console.log(`History for ${this.namespace}: ${texts}`)
        return texts
    }

    saveText(text) {
        if (!text) {
            return
        }
        const texts = this.getTexts()
        texts.push(text)
        console.log(`Saving ${text} in ${this.namespace}`)
        localStorage.setItem(this.namespace, JSON.stringify(_.uniq(texts)))
    }

    clear() {
        localStorage.removeItem(this.namespace)
    }
}

export default TextHistory
export {TextHistory, getAllNamespaces }