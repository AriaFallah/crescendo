const { spawn } = require('child_process')
import React, { Component } from 'react'
import { Link } from 'react-router'

export default class Main extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  componentWillMount() {
    this.leap =
      spawn('node', ['/Users/Developer/workspace/hackathons/hacktech/leap/leap.js'])
    this.keyboard =
      spawn('python', ['/Users/Developer/workspace/hackathons/hacktech/sensor/keyboard.py'])

    this.leap.stdout.on('data', (data) => {
      const message = data.toString()
      if (message[0] === '?') this.setState({ leapMessage: message.slice(2) })
    })
    this.leap.stderr.on('data', (data) => {
      this.setState({ stderr: data.toString() })
    })
    this.leap.on('close', (code) => {
      console.log(`Leap exited with code ${code}`)
    })

    this.keyboard.stdout.on('data', (data) => {
      const message = data.toString()
      if (message === 'ready!\n') {
        this.setState({ keyboardReady: true })
      }
    })
    this.keyboard.stderr.on('data', (data) => {
      console.log(`error: ${data}`)
    })
    this.keyboard.on('close', (code) => {
      console.log(`Keyboard exited with code ${code}`)
    })
  }

  componentWillUnmount() {
    this.leap.kill()
    this.keyboard.kill()
  }

  sendResponse() {
    console.log(this.state.responseValue)
    this.leap.stdin.setEncoding('utf-8')
    this.leap.stdout.pipe(process.stdout)
    this.leap.stdin.write(`console.log(${this.state.responseValue})\n`)
  }

  render() {
    return (
      <section className="centered">
        <nav className="reset">
          <Link to="/">
            <button className="ui button red">Reset</button>
          </Link>
        </nav>

        <figure className="status">
          <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg"
            x="0px" y="0px" width="512px" height="512px" viewBox="0 0 512 512"
            enable-background="new 0 0 512 512"
          >
          <g>
            <circle cx="255.811" cy="285.309" r="75.217" />
            <path d="M477,137H352.718L349,108c0-16.568-13.432-30-30-30H191c-16.568,0-30,13.432-30,
            30l-3.718,29H34c-11.046,0-20,8.454-20,19.5v258c0,11.046,8.954,20.5,20,20.5h443c11.046,0,
            20-9.454,20-20.5v-258C497, 145.454,488.046,137,477,137z M255.595,408.562c-67.928,
            0-122.994-55.066-122.994-122.993c0-67.928,55.066-122.994,122.994-122.994 c67.928,0,
            122.994,55.066,122.994,122.994C378.589,353.495,323.523,408.562,255.595,408.562z M474,
            190H369v-31h105V190z"
            />
          </g>
          </svg>
          <svg
            className={this.state.keyboardReady ? 'active' : 'broken'}
            version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" x="0px" y="0px"
            width="512px" height="512px" viewBox="0 0 512 512" enable-background="new 0 0 512 512"
          >
            <path fill-rule="evenodd" clip-rule="evenodd"
              d="M416,0H96C78.313,0,64,14.328,64,32v448c0,17.688,14.313,32,32,32
              h320c17.688,0,32-14.313,32-32V32C448,14.328,433.688,0,416,0z M256,
              496c-13.25,0-24-10.75-24-24s10.75-24,24-24s24,10.75,24,24
              S269.25,496,256,496z M400,432H112V48h288V432z"
            />
          </svg>
        </figure>

        <div>
          <question className="subheading">{this.state.leapMessage}</question>
        </div>

        {this.state.leapMessage
          ? <form>
              <input
                onKeyUp={function(e) { console.log(e) }}
                className="centered fadein" type="text"
              />
            </form>
          : <div className="ui loader active inverted"></div>}
      </section>
    )
  }
}
