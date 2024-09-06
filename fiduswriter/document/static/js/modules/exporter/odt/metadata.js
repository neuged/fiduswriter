import {escapeText} from "../../common"


export class ODTExporterMetadata {
    constructor(xml, styles, metadata) {
        this.xml = xml
        this.styles = styles
        this.metadata = metadata
        this.metaXml = false
    }

    init() {
        return this.xml.getXml("meta.xml").then(
            metaXml => {
                this.metaXml = metaXml
                this.addMetadata()
                return Promise.resolve()
            }
        )
    }


    addMetadata() {
        const metaEl = this.metaXml.querySelector("meta")

        // Title
        let titleEl = this.metaXml.querySelector("title")
        if (!titleEl) {
            metaEl.insertAdjacentHTML("beforeEnd", "<dc:title></dc:title>")
            titleEl = this.metaXml.querySelector("title")
        }
        titleEl.innerHTML = escapeText(this.metadata.title)

        // Authors
        const authors = this.metadata.authors.map(author => {
            const nameParts = []
            if (author.firstname) {
                nameParts.push(author.firstname)
            }
            if (author.lastname) {
                nameParts.push(author.lastname)
            }
            if (!nameParts.length && author.institution) {
                // We have an institution but no names. Use institution as name.
                nameParts.push(author.institution)
            }
            return nameParts.join(" ")
        })

        const initialAuthor = authors.length ?
            escapeText(authors[0]) :
            gettext("Unknown")
        // TODO: We likely want to differentiate between first and last author.
        const lastAuthor = initialAuthor

        let lastAuthorEl = this.metaXml.querySelector("creator")
        if (!lastAuthorEl) {
            metaEl.insertAdjacentHTML("beforeEnd", "<dc:creator></dc:creator>")
            lastAuthorEl = this.metaXml.querySelector("creator")
        }
        lastAuthorEl.innerHTML = lastAuthor
        let initialAuthorEl = this.metaXml.querySelector("initial-creator")
        if (!initialAuthorEl) {
            metaEl.insertAdjacentHTML("beforeEnd", "<meta:initial-creator></meta:initial-creator>")
            initialAuthorEl = this.metaXml.querySelector("initial-creator")
        }
        initialAuthorEl.innerHTML = initialAuthor

        // Keywords
        // Remove all existing keywords
        const keywordEls = this.metaXml.querySelectorAll("keywords")
        keywordEls.forEach(
            keywordEl => keywordEl.parentNode.removeChild(keywordEl)
        )
        // Add new keywords
        const keywords = this.metadata.keywords
        keywords.forEach(
            keyword => metaEl.insertAdjacentHTML("beforeEnd", `<meta:keyword>${escapeText(keyword)}</meta:keyword>`)
        )

        // language
        // LibreOffice seems to ignore the value set in metadata and instead uses
        // the one set in default styles. So we set both.
        this.styles.setLanguage(this.metadata.language)
        let languageEl = this.metaXml.querySelector("language")
        if (!languageEl) {
            metaEl.insertAdjacentHTML("beforeEnd", "<dc:language></dc:language>")
            languageEl = this.metaXml.querySelector("language")
        }
        languageEl.innerHTML = this.metadata.language
        // time
        const date = new Date()
        const dateString = date.toISOString().split(".")[0]
        const createdEl = this.metaXml.querySelector("creation-date")
        createdEl.innerHTML = dateString
        let dateEl = this.metaXml.querySelector("date")
        if (!dateEl) {
            metaEl.insertAdjacentHTML("beforeEnd", "<dc:date></dc:date>")
            dateEl = this.metaXml.querySelector("date")
        }
        dateEl.innerHTML = `${dateString}.000000000`
    }

}
