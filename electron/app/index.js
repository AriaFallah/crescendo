import React from 'react'
import { render } from 'react-dom'
import { Router, Route, hashHistory } from 'react-router'
import Home from './components/Home'
import Main from './components/Main'
import './app.global.css'

render(
  <Router history={hashHistory}>
    <Route path="/" component={Home} />
    <Route path="/app" component={Main}  />
  </Router>,
  document.getElementById('root')
)
