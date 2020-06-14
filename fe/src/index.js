import React from 'react';
import ReactDOM from 'react-dom';
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
} from "react-router-dom";
import Login from './component/Login'
import Reg from "./component/Reg";
import ArticleList from './component/ArticleList'


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
                <ul>
                    <li><Link to="/">主页</Link></li>
                    <li><Link to="/login">登陆</Link></li>
                    <li><Link to="/reg">注册</Link></li>
                    <li><Link to="/about">关于</Link></li>
                    <li><Link to="/list">文章列表</Link></li>
                </ul>

                <Route path="/about" component={About}/>
                <Route path="/login" component={Login}/>
                <Route path="/reg" component={Reg}/>
                <Route path="/list" component={ArticleList}/>
                <Route exact path="/" component={Home}/>
            </div>
        </Router>
    );
}

ReactDOM.render(
    <App/>,
    document.getElementById('root')
);