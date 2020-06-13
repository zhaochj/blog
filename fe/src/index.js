import React from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";


function Home() {
  return (
    <div>
      <h2>Home</h2>
    </div>
  );
}

function About() {
  return (
    <div>
      <h2>About</h2>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div>
           <Route exact path="/">
            <Home />
          </Route>
          <Route path="/about">
            <About />
          </Route>
      </div>
    </Router>
  );
}

ReactDOM.render(
<App />,
document.getElementById('root')
);