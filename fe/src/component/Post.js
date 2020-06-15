import React from 'react';
import {Link} from 'react-router-dom';
import {Redirect} from 'react-router'
import postService from "../service/post";
import {observer} from 'mobx-react';
import {message} from "antd";
import inject from '../inject';
import 'antd/lib/list/style';
import { Card } from 'antd';
import 'antd/lib/card/style';


const service = postService;

@inject({service})
@observer
export default class Post extends React.Component {
    constructor(props) {
        super(props);
        let post_id = this.props.match.params.id;  // 拿到 http://url/post/2  这里的 2
        this.props.service.getPost(post_id);
    }


    render() {
        // 有错误信息时，页面友好提示
        if (this.props.service.errMsg) {
            message.error(this.props.service.errMsg, 3, () => {this.props.service.errMsg=""});
        }

        return (
            <Card title={this.props.service.post.title} bordered={false} style={{ width: 300 }}>
                <p>{this.props.service.post.author} {new Date(this.props.service.post.postdate * 1000).toLocaleDateString()}</p> {/*js中的时间戳与数据库中的相差1000倍*/}
                <p>{this.props.service.post.content}</p>
            </Card>
        )
    }
}