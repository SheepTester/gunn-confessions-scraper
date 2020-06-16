// ==UserScript==
// @name         Gunn Confessions scraper v2
// @namespace    https://sheeptester.github.io/
// @version      1.0
// @description  Searches Gunn Confessions within a date range; start by doing ?start=<date>
// @author       SheepTester
// @match        *://www.facebook.com/page/gunnconfessions/search/*
// @grant        none
// ==/UserScript==

(async function () {
    'use strict'

    const INTERVAL = 7 // One week interval

    const foundKey = '[gunn-confessions-scraper] v2.found'

    const mainSelector = '[role="main"]'
    const loadingSelector = '[role="progressbar"]'
    const linkSelector = 'a[href^="https://www.facebook.com/gunnconfessions/posts/"'
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
                    start_month: startPieces.slice(0, 1).join('-'),
                    start_day: startPieces.join('-'),
                    end_year: endPieces[0],
                    end_month: endPieces.slice(0, 1).join('-'),
                    end_day: endPieces.join('-')
                })
            })
        }))
    }

    const confessionNumberRegex = /(?:^|\n)(\d+)\. /
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
        params.set('filter', createFilter({
            start,
            end
        }))
        params.delete('start')
        window.location = '?' + params
    }

    const scroller = document.scrollingElement
    while (!document.querySelector(mainSelector) || document.querySelector(loadingSelector) || scroller.scrollTop + scroller.clientHeight < scroller.scrollHeight - 5) {
        scroller.scrollTop = scroller.scrollHeight
        await delay(200)
    }

    const links = document.querySelectorAll(linkSelector)
    const newFound = Object.fromEntries(Array.from(links, link => [
        getConfessionNumber(link.querySelector(contentSelector).childNodes[1].nodeValue),
        getPostId(link.href)
    ]))
    console.log(JSON.stringify(newFound, null, 2))

    const found = JSON.parse(localStorage.getItem(foundKey)) || {}
    Object.assign(found, newFound)
    localStorage.setItem(foundKey, JSON.stringify(found))

    const { start, end } = parseFilter(params.get('filter'))
    start.setUTCDate(start.getUTCDate() - INTERVAL)
    end.setUTCDate(end.getUTCDate() - INTERVAL)
    params.set('filter', createFilter({ start, end }))
    window.location = '?' + params
})()
