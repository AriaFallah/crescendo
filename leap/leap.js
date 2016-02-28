'use strict'

const leap     = require('leapjs')
const midi     = require('midi')
const inquirer = require('inquirer')
const co       = require('co')
const Promise  = require('bluebird')

const output = new midi.output()
output.openVirtualPort('Leap')

const questions = [{
  type: "input",
  name: "x",
  message: "Assigning x-axis (left-right): Press enter after you have setup the connection (or s to skip)."
}, {
  type: "input",
  name: "y",
  message: "Assigning y-axis (up-down): Press enter after you have setup the connection (or s to skip).",
}, {
  type: "input",
  name: "z",
  message: "Assigning z-axis (forward-backward): Press enter after you have setup the connection (or s to skip).",
}];

// Use co to synchronously prompt for questions
co(function* () {
  for (const question of questions) {
    const answer = yield new Promise((resolve) => inquirer.prompt(question, resolve))
    if      (answer.x !== undefined && answer.x !== 's') output.sendMessage([0xB0, 9,  0])
    else if (answer.y !== undefined && answer.y !== 's') output.sendMessage([0xB0, 3,  0])
    else if (answer.z !== undefined && answer.z !== 's') output.sendMessage([0xB0, 14, 0])
  }
}).then(() => {
  const controller = leap.loop(function(frame) {
    if(frame.hands.length > 0) {
      const hand = frame.hands[0]
      const position = hand.palmPosition

      let modx = Math.round((((position[0] + 150) / 300) * 127), 0)
      let mody = Math.round((((position[1] -  45) / 400) * 127), 0)
      let modz = Math.round((((position[2] + 150) / 300) * 127), 0)

      if (modx > 127) modx = 127
      if (mody > 127) mody = 127
      if (modz > 127) modz = 127
      if (modx <   0) modx = 0
      if (mody <   0) mody = 0
      if (modz <   0) modz = 0

      if (hand.timeVisible !== 0) {
        output.sendMessage([0xB0,  3,  mody])
        output.sendMessage([0xB0,  9,  modx])
        output.sendMessage([0xB0, 14,  modz])
        console.log(modx, mody, modz)
      }
    }
  })
})
