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
import Post from "./component/Post";
import { Menu, Icon } from 'antd';
import 'antd/lib/menu/style';


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
                <Menu mode="horizontal">
                    <Menu.Item key="home">
                        <Link to="/"><Icon type="home"/>主页</Link>
                    </Menu.Item>
                    <Menu.Item key="login">
                        <Link to="/login">登陆</Link>
                    </Menu.Item>
                    <Menu.Item key="reg">
                        <Link to="/reg">注册</Link>
                    </Menu.Item>
                    <Menu.Item key="list">
                        <Link to="/post">文章列表</Link>
                    </Menu.Item>
                    <Menu.Item key="about">
                        <Link to="/about">关于</Link>
                    </Menu.Item>
                </Menu>

                <Route path="/about" component={About}/>
                <Route path="/login" component={Login}/>
                <Route path="/reg" component={Reg}/>
                <Route exact path="/post" component={ArticleList}/>
                <Route exact path="/post/:id" component={Post}/>
                <Route exact path="/" component={Home}/>
            </div>
        </Router>
    );
}

ReactDOM.render(
    <App/>,
    document.getElementById('root')
);