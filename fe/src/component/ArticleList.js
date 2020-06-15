import React from 'react';
import {Link} from 'react-router-dom';
import {Redirect} from 'react-router'
import '../css/login.css'
import postService from "../service/post";
import {observer} from 'mobx-react';
import {message} from "antd";
import inject from '../inject';
import { List, Typography } from 'antd';
import 'antd/lib/list/style';


const service = postService;

@inject({service})
@observer
export default class ArticleList extends React.Component {
    constructor(props) {
        super(props);
        this.params = new URLSearchParams(this.props.location.search);  // 这个数据结构能解析url中的params
        this.props.service.list(this.params.get('page'), this.params.get('size'))
    }



    render() {
        // 有错误信息时，页面友好提示
        if (this.props.service.errMsg) {
            message.error(this.props.service.errMsg, 3, () => {this.props.service.errMsg=""});
        }

        // data数据从何来？当访问http://url/post/时后端返回
        let data = this.props.service.posts;
        if (data.length) {
            return (
                <List
                    size="small"
                    bordered
                    dataSource={data}
                    renderItem={item => <List.Item>
                        <Link to={'/post/' + item.post_id}>{item.title}</Link>
                    </List.Item>}
                />
            )
        }
        else {
            return <div> </div>
        }
    }
}