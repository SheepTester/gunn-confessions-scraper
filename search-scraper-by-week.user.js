// ==UserScript==
// @name         Gunn Confessions scraper v2
// @namespace    https://sheeptester.github.io/
// @version      1.0
// @description  Searches Gunn Confessions within a date range; start by doing ?start=<date>
// @author       SheepTester
// @match        *://www.facebook.com/page/gunnconfessions/search/*
// @grant        GM_setValue
// @grant        GM_getValue
// ==/UserScript==

(async function () {
    'use strict'

    document.zGM_getValue = (...args) => GM_getValue(...args)
    document.zGM_setValue = (...args) => GM_setValue(...args)

    // Thanks Tim! https://www.facebook.com/page/1792991304081448/search?q=Gunn&filters=eyJycF9jcmVhdGlvbl90aW1lIjoie1wibmFtZVwiOlwiY3JlYXRpb25fdGltZVwiLFwiYXJnc1wiOlwie1xcXCJzdGFydF95ZWFyXFxcIjpcXFwiMjAyMFxcXCIsXFxcInN0YXJ0X21vbnRoXFxcIjpcXFwiMjAyMC0xXFxcIixcXFwiZW5kX3llYXJcXFwiOlxcXCIyMDIwXFxcIixcXFwiZW5kX21vbnRoXFxcIjpcXFwiMjAyMC0xXFxcIixcXFwic3RhcnRfZGF5XFxcIjpcXFwiMjAyMC0xLTFcXFwiLFxcXCJlbmRfZGF5XFxcIjpcXFwiMjAyMC0xLTdcXFwifVwifSJ9
    // Start point: https://www.facebook.com/page/gunnconfessions/search/?start=2019-03-12

    const INTERVAL = 5
    const END = new Date(Date.UTC(2019, 2 - 1, 28)) // https://www.facebook.com/gunnconfessions/posts/2019518851428691

    const foundKey = '[gunn-confessions-scraper] v2.found'

    const mainSelector = '[role="main"]'
    const loadingSelector = '[role="main"] [role="progressbar"]'
    const linkSelector = '[role="main"] a[href^="https://www.facebook.com/gunnconfessions/posts/"]'
    const contentSelector = '.l9j0dhe7.stjgntxs.ni8dbmo4'

    function stringToDateUTC (str) {
        const [year, month, date] = str.split('-')
        return new Date(Date.UTC(+year, +month - 1, +date))
    }

    function dateUTCToArray(date) {
        return [date.getUTCFullYear(), date.getUTCMonth() + 1, date.getUTCDate()]
            .map(n => n.toString())
    }

    function parseFilter (filters) {
        const { start_day: start, end_day: end } = JSON.parse(JSON.parse(JSON.parse(atob(filters)).rp_creation_time).args)
        return { start: stringToDateUTC(start), end: stringToDateUTC(end) }
    }

    function createFilter ({ start, end }) {
        const startPieces = dateUTCToArray(start)
        const endPieces = dateUTCToArray(end)
        return btoa(JSON.stringify({
            rp_creation_time: JSON.stringify({
                name: 'creation_time',
                args: JSON.stringify({
                    start_year: startPieces[0],
                    start_month: startPieces.slice(0, 2).join('-'),
                    end_year: endPieces[0],
                    end_month: endPieces.slice(0, 2).join('-'),
                    start_day: startPieces.join('-'),
                    end_day: endPieces.join('-')
                })
            })
        }))
    }

    const confessionNumberRegex = /(?:^|\n)(\d+)\.\s/
    function getConfessionNumber (content) {
        const match = content.match(confessionNumberRegex)
        return match ? match[1] : null
    }

    const getPostIdRegex = /\/posts\/(\d+)/
    function getPostId (link) {
        const match = link.match(getPostIdRegex)
        return match ? match[1] : null
    }

    const delay = time => new Promise(resolve => setTimeout(resolve, time))

    const params = new URL(window.location).searchParams

    if (params.get('start')) {
        const end = stringToDateUTC(params.get('start'))
        const start = new Date(end)
        start.setUTCDate(end.getUTCDate() - INTERVAL)
        params.set('q', 'Gunn')
        params.set('filters', createFilter({
            start,
            end
        }))
        params.delete('start')
        window.location = '?' + params
    }

    const scroller = document.scrollingElement
    while (!document.querySelector(mainSelector) || document.querySelector(loadingSelector) || scroller.scrollTop + scroller.clientHeight < scroller.scrollHeight - 5) {
        scroller.scrollTop = scroller.scrollHeight
        await delay(500)
    }

    const links = document.querySelectorAll(linkSelector)
    const newFound = Object.fromEntries(Array.from(links, link => {
        const postId = getPostId(link.href)
        return [
            getConfessionNumber(link.querySelector(contentSelector).childNodes[1].nodeValue) || `worrying_${postId}`,
            postId
        ]
    }))
    console.log(JSON.stringify(newFound, null, 2))

    const found = JSON.parse(GM_getValue(foundKey, null)) || {}
    Object.assign(found, newFound)
    GM_setValue(foundKey, JSON.stringify(found))

    const { start, end } = parseFilter(params.get('filters'))
    console.log('^', start.toISOString(), end.toISOString())
    start.setUTCDate(start.getUTCDate() - INTERVAL)
    end.setUTCDate(end.getUTCDate() - INTERVAL)
    params.set('filters', createFilter({ start, end }))
    if (start >= END) window.location = '?' + params
})()
