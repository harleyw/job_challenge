// 引入Vue和创建应用实例
const { createApp, ref, onMounted, onUnmounted, getCurrentInstance } = Vue

// 创建Vue应用
const app = createApp({
    setup() {
        // 响应式状态
        const question = ref('')
        const answer = ref('')
        const showAnswer = ref(false)
        const isLoading = ref(false)
        const errorMessage = ref('')
        let abortController = ref(null)
        const userScrolled = ref(false)  // 跟踪用户是否手动滚动
        const showLogs = ref(true)  // 控制日志区域的显示/隐藏

        // 带时间戳的日志函数
        const timestampLog = (level, ...args) => {
            const timestamp = new Date().toISOString();
            if (level === 'error') {
                console.error(`[${timestamp}]`, ...args);
            } else {
                console.log(`[${timestamp}]`, ...args);
            }
        }

        // 获取组件实例并保存
        const instance = getCurrentInstance()
        if (instance) {
            timestampLog('log', '成功获取组件实例')
        } else {
            timestampLog('error', '未能在setup函数中获取组件实例')
        }

        // 提交问题函数
        const submitQuestion = () => {
            // 取消任何正在进行的请求
            cancelRequest()

            if (!question.value.trim()) {
                errorMessage.value = '请输入有效的问题'
                return
            }

            // 重置状态
            answer.value = ''
            showAnswer.value = true
            isLoading.value = true
            errorMessage.value = ''

            // 创建AbortController用于取消请求
            abortController.value = new AbortController()
            const signal = abortController.value.signal

            let rawMarkdownBuffer = ''

            fetch('http://127.0.0.1:5000/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question.value }),
                signal
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP错误! 状态码: ${response.status}`)
                }

                if (!response.body) {
                    throw new Error('响应体为空')
                }

                const reader = response.body.getReader()
                const decoder = new TextDecoder('utf-8')
                let buffer = ''

                // 处理流式响应的递归函数 - 改为异步函数以支持await
                const processStream = async ({ done, value }) => {
                    if (done) {
                        isLoading.value = false
                        
                        timestampLog('log', '---Done--- \nMarkdown数据: ', rawMarkdownBuffer)
                        // 所有数据接收完毕，将原始内容替换为Markdown格式
                        answer.value = marked.parse(rawMarkdownBuffer)
                        rawMarkdownBuffer = ''
                        
                        // 强制更新UI以显示Markdown解析后的内容
                        Vue.nextTick(() => {
                            instance.proxy.$forceUpdate()
                            timestampLog('log', 'Markdown内容已更新')
                            if(!userScrolled.value) {
                                autoScroll()  // 自动滚动到最新内容
                            }
                        })
                        return
                    }

                    buffer = decoder.decode(value, { stream: true })
                    timestampLog('log', '接收原始数据:', buffer)
                    const words = buffer.split('\n\n')

                    // 处理单词级数据
                    for (const word of words) {
                        timestampLog('log', 'word 原始数据:', word)
                        let dataStr = ''
                        if (word.startsWith('data: ')) {
                            dataStr = word.slice(6) // 移除 'data: '
                        } else {
                            dataStr = word
                        }

                        try {
                            // 处理单词级数据
                            timestampLog('log', '收到单词:', dataStr);
                            // 检查是否是团队标识
                            if (dataStr.startsWith('[')) {
                                // 新的团队消息，添加换行和标识
                                answer.value += '<br>' + dataStr + ' '
                                rawMarkdownBuffer += '\n---\n\n' + dataStr
                            } else if(dataStr.endsWith('<br>')) {
                                // 换行符，添加到Markdown缓冲区
                                answer.value += dataStr
                                rawMarkdownBuffer += dataStr.slice(0, -4) + '\n'
                            } else {
                                // 普通单词，添加到当前行
                                answer.value += dataStr + ' ';
                                rawMarkdownBuffer += dataStr + ' '
                            }
                        } catch (error) {
                            timestampLog('error', '数据处理错误:', error)
                        }

                        // 每行处理完后，立即更新UI
                        // 使用Vue.nextTick确保DOM更新完成
                        Vue.nextTick(() => {
                            // 强制组件更新
                            instance.proxy.$forceUpdate()
                            if(!userScrolled.value) {
                                autoScroll()  // 自动滚动到最新内容
                            }
                        })
                        // 短暂延迟确保更新生效
                        await new Promise(resolve => setTimeout(resolve, 80))
                    }

                    // 继续读取流
                    return reader.read().then(processStream)
                }
                
                // 开始处理流
                return reader.read().then(processStream)
            })
            .catch(error => {
                if (error.name !== 'AbortError') {
                    console.error('提交问题时出错:', error)
                    errorMessage.value = '抱歉，获取答案时出错了。'
                } else {
                    console.log('请求已被用户取消')
                }
                isLoading.value = false
            })
        }

        // 取消请求函数
        const cancelRequest = () => {
            if (abortController.value) {
                abortController.value.abort()
                abortController.value = null
                isLoading.value = false
                console.log('请求已取消')
            }
        }

        // 自动滚动函数
        const autoScroll = () => {
            if (!userScrolled.value) {
                const answerContainer = document.querySelector('.answer-container')
                if (answerContainer) {
                    //timestampLog('log', '滚动前 - scrollTop:', answerContainer.scrollTop, 'scrollHeight:', answerContainer.scrollHeight)
                    // 使用requestAnimationFrame确保滚动操作在浏览器的下一个动画帧中执行
                    requestAnimationFrame(() => {
                        answerContainer.scrollTop = answerContainer.scrollHeight
                        //timestampLog('log', '滚动后 - scrollTop:', answerContainer.scrollTop)
                    })
                } else {
                    timestampLog('error', '未找到.answer-container元素')
                }
            }
        }

        // 组件挂载时添加滚动事件监听器
        onMounted(() => {
            const answerContainer = document.querySelector('.answer-container')
            if (answerContainer) {
                const handleScroll = () => {
                    // 检查用户是否手动滚动
                    if (answerContainer.scrollTop + answerContainer.clientHeight < answerContainer.scrollHeight - 10) {
                        userScrolled.value = true
                        timestampLog('log', '用户手动滚动，禁用自动滚动')
                    } else if (answerContainer.scrollTop + answerContainer.clientHeight >= answerContainer.scrollHeight - 10) {
                        userScrolled.value = false
                        timestampLog('log', '滚动到底部，启用自动滚动')
                    } else {
                        timestampLog('log', '滚动过程中')
                    }
                }
                answerContainer.addEventListener('scroll', handleScroll)

                // 组件卸载时移除事件监听器
                onUnmounted(() => {
                    answerContainer.removeEventListener('scroll', handleScroll)
                })
            }
        })

        // 组件卸载时取消请求
        onUnmounted(() => {
            cancelRequest()
        })

        // 返回暴露给模板的状态和方法
        return {
            question,
            answer,
            showAnswer,
            isLoading,
            errorMessage,
            submitQuestion,
            showLogs
        }
    }
})

// 挂载应用
app.mount('#app')