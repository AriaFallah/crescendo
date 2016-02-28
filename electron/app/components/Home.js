import React from 'react'
import { Link } from 'react-router'

export default () =>
  <div className="centered">
    <img className="logo" src="logo.png" />
    <h3 className="subheading">Making Music Intuitive</h3>
    <Link to="/app">
      <button className="ui button fadein">Get Started</button>
    </Link>
  </div>
