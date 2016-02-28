import React, { Component } from 'react'
import { render } from 'react-dom'
import { Router, Route, hashHistory, Link } from 'react-router'
import './app.global.css'

const HomePage = () =>
  <div className="container">
    <img className="logo" src="logo.png" />
    <h3 className="subheading">Making Music Intuitive</h3>
    <Link to="/configure">
      <button className="ui button">Get Started</button>
    </Link>
  </div>

class ConfigurePage extends Component {
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
    <Route path="/app" />
  </Router>,
  document.getElementById('root')
)
