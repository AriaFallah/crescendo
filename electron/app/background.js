import { app, BrowserWindow } from 'electron'
import devHelper from './vendor/electron_boilerplate/dev_helper'
import windowStateKeeper from './vendor/electron_boilerplate/window_state'

import env from './env'

// Preserver of the window size and position between app launches.
const mainWindowState = windowStateKeeper('main', {
  width: 1000,
  height: 600
})

app.on('ready', () => {
  const mainWindow = new BrowserWindow({
    x: mainWindowState.x,
    y: mainWindowState.y,
    width: mainWindowState.width,
    height: mainWindowState.height
  })

  if (mainWindowState.isMaximized) {
    mainWindow.maximize()
  }

  if (env.name === 'test') {
    mainWindow.loadURL(`file://${__dirname}/spec.html`)
  } else {
    mainWindow.loadURL(`file://${__dirname}/app.html`)
  }

  if (env.name !== 'production') {
    devHelper.setDevMenu()
    mainWindow.openDevTools()
  }

  mainWindow.on('close', () => mainWindowState.saveState(mainWindow))
})

app.on('window-all-closed', () => app.quit())
