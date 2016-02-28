const spawn = require('child_process').spawn
import React, { Component } from 'react'
import { render } from 'react-dom'
import { Router, Route, hashHistory, Link } from 'react-router'
import './app.global.css'

const HomePage = () =>
  <div className="container">
    <img className="logo" src="logo.png" />
    <h3 className="subheading">Making Music Intuitive</h3>
    <Link to="/configure">
      <button className="ui button animate">Get Started</button>
    </Link>
  </div>

class ConfigurePage extends Component {
  componentWillMount() {
    console.log('Trying to get LEAP to work')
    this.p = spawn('python', ['/Users/Developer/workspace/hackathons/hacktech/leap/track.py'])
    this.p.stdout.on('data', (data) => {
      console.log(`${data}`)
    })
    this.p.stderr.on('data', (data) => {
      console.log(`error: ${data}`)
    })
    this.p.on('close', (code) => {
      console.log(`child process exited with code ${code}`)
    })
  }
  componentWillUnmount() {
    this.p.kill()
  }
  render() {
    return (
      <div>
        <Link to="/">HOME</Link>
        <Link to="/app">APP</Link>
      </div>
    )
  }
}

class AppPage extends Component {
  componentWillMount() {
    console.log('Spawning Keyboard')
    this.p = spawn('python', ['/Users/Developer/workspace/hackathons/hacktech/sensor/sensor2midi.py'])
    this.p.stdout.on('data', (data) => {
      console.log(`${data}`)
    })
    this.p.stderr.on('data', (data) => {
      console.log(`error: ${data}`)
    })
    this.p.on('close', (code) => {
      console.log(`child process exited with code ${code}`)
    })
  }
  componentWillUnmount() {
    this.p.kill()
  }
  render() {
    return (
      <div>
        <Link to="/">HOME</Link>
      </div>
    )
  }
}

render(
  <Router history={hashHistory}>
    <Route path="/" component={HomePage} />
    <Route path="/configure" component={ConfigurePage}  />
    <Route path="/app" component={AppPage} />
  </Router>,
  document.getElementById('root')
)
