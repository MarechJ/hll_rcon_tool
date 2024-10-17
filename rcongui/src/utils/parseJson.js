export const parseJson = async response => {
    const text = await response.text()
    try {
        const json = JSON.parse(text)
        return json
    } catch (err) {
        return { error: response.statusText }
    }
}