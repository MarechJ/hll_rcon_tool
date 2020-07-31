import _ from 'lodash'
import { startsWith } from 'lodash/string'


const PREFIX = "autocomplete_"

const getAllNamespaces = () => (
    Object.keys(localStorage).filter(e => startsWith(e, PREFIX)).map(v => v.replace(PREFIX, '')).filter(v => !v.includes('undefined'))
)

class TextHistory {
    constructor(namespace) {
        this.namespace = PREFIX + namespace
    }

    getTexts() {
        let texts = localStorage.getItem(this.namespace)
        
        if (!texts) {
            texts = []
            localStorage.setItem(this.namespace, JSON.stringify(texts))
        } else {
            texts = JSON.parse(texts)
        }
       
        return texts
    }

    deleteTextByIdx(index) {
        const texts = this.getTexts()
        console.log("Deleting index", index, texts.splice(index, index + 1))
        localStorage.setItem(this.namespace, JSON.stringify(texts))
    }

    saveText(text) {
        if (!text) {
            return
        }
        const texts = this.getTexts()
        texts.push(text)
        localStorage.setItem(this.namespace, JSON.stringify(_.uniq(texts)))
    }

    clear() {
        localStorage.removeItem(this.namespace)
    }
}

export default TextHistory
export {TextHistory, getAllNamespaces }