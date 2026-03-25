import { TokenStore } from '../xal'
import Store from 'electron-store'
import { app } from 'electron'
import fs from 'fs'
import path from 'path'

export default class AuthTokenStore extends TokenStore {

    private _store: Store

    constructor() {
        super()
        // 确保存储目录存在
        this.ensureUserDataDir()
        this._store = new Store()
    }

    private ensureUserDataDir() {
        try {
            const userDataPath = app.getPath('userData')
            if (!fs.existsSync(userDataPath)) {
                fs.mkdirSync(userDataPath, { recursive: true })
            }
        } catch (error) {
            console.error('Failed to create user data directory:', error)
        }
    }

    load() {
        try {
            const tokens = this._store.get('user.tokenstore', '{}') as string
            this.loadJson(tokens)
            return true
        } catch (error) {
            console.error('Failed to load tokens:', error)
            return false
        }
    }

    save() {
        try {
            const data = JSON.stringify({
                userToken: this._userToken?.data,
                sisuToken: this._sisuToken?.data,
                jwtKeys: this._jwtKeys,
                tokenUpdateTime: Date.now(),
            })

            this._store.set('user.tokenstore', data)
        } catch (error) {
            console.error('Failed to save tokens:', error)
        }
    }

    getTokenUpdateTime() {
        try {
            const tokens = this._store.get('user.tokenstore', '{}') as string
            this.loadJson(tokens)
            return this._tokenUpdateTime
        } catch (error) {
            console.error('Failed to get token update time:', error)
            return 0
        }
    }

    clear() {
        try {
            this._store.delete('user.tokenstore')
        } catch (error) {
            console.error('Failed to clear tokens:', error)
        }
        this._userToken = undefined
        this._sisuToken = undefined
        this._jwtKeys = undefined
    }

    removeAll() {
        this._userToken = undefined
        this._sisuToken = undefined

        try {
            this._store.delete('user.tokenstore')
        } catch (error) {
            console.error('Failed to remove all tokens:', error)
        }
    }
}