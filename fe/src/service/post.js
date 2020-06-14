import React from 'react';
import axios from 'axios';
import store from 'store';
import {observable} from 'mobx'


class PostService {
    @observable posts = [];  // 博文列表
    @observable pagination = {page: 1, size: 20, count: 0, page_count: 0};  // 分页信息
    @observable errMsg = "";

    list(page = 1, size = 10) {
        axios.get('/api/post/')
            .then(response => {
                console.log(response);
                this.posts = response.data.posts;
                this.pagination = response.data.pagination;
            })
            .catch(error => {
                console.log(error);
                this.errMsg = "文章列表加载失败"
            });
    }
}

const postService = new PostService();
export default postService