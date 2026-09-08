// ==UserScript==
// @name         ITSoft CRM2 AI Assistant
// @namespace    http://tampermonkey.net/
// @version      1.4
// @description  Автоматизация создания задач и ответов в CRM2 с помощью Gemini API
// @author       Sergei Tikhomirov
// @match        https://crm.itsoft.ru/*
// @connect      crm-ai-assistant.onrender.com
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function () {
    'use strict';
  
    const BACKEND_URL = 'https://crm-ai-assistant.onrender.com/api/process-thread';
    const API_SECRET = 'my_super_secret_key_123';
  
    function parseCRMContext() {
      const h1Element = document.querySelector('h1.title') || document.querySelector('h1');
      const h1Text = h1Element ? h1Element.innerText.trim() : '';
      const branchIdMatch = h1Text.match(/\d+/) || window.location.pathname.match(/\d+/);
  
      return {
        branch_id: branchIdMatch ? branchIdMatch[0] : '',
        h1_title: h1Text
      };
    }
  
    function extractTextFromHTML(htmlString) {
      if (!htmlString) return '';
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlString, 'text/html');
      return doc.body.innerText.trim();
    }
  
    function parseVisibleMessages() {
      const messages = [];
      const messageNodes = document.querySelectorAll('.js-branch-item');
  
      messageNodes.forEach((node) => {
        if (node.offsetParent === null) return;
  
        const headBoxes = node.querySelectorAll('.branch__head-box');
        let author = 'Неизвестно';
        let date = '';
  
        headBoxes.forEach((box) => {
          const text = box.innerText.trim();
          if (text.startsWith('From:')) {
            author = text.replace('From:', '').trim();
          } else if (/\d{4}-\d{2}-\d{2}/.test(text)) {
            date = text.split('\n')[0].trim();
          }
        });
  
        let messageText = '';
        const iframe = node.querySelector('.branch__box iframe');
        const textDiv = node.querySelector('.branch__text');
  
        if (iframe && iframe.getAttribute('srcdoc')) {
          messageText = extractTextFromHTML(iframe.getAttribute('srcdoc'));
        } else if (textDiv && textDiv.innerText.trim()) {
          messageText = textDiv.innerText.trim();
        }
  
        if (messageText) {
          messages.push({
            author: author,
            date: date,
            text: messageText
          });
        }
      });
  
      return messages;
    }
  
    function showCopyModal(title, textContent) {
      const existingModal = document.getElementById('ai-result-modal');
      if (existingModal) existingModal.remove();
  
      const overlay = document.createElement('div');
      overlay.id = 'ai-result-modal';
      overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0, 0, 0, 0.5); z-index: 100000;
        display: flex; align-items: center; justify-content: center;
        font-family: Arial, sans-serif;
      `;
  
      const modal = document.createElement('div');
      modal.style.cssText = `
        background: #ffffff; width: 600px; max-width: 90vw; max-height: 85vh;
        border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        display: flex; flex-direction: column; overflow: hidden;
      `;
  
      const header = document.createElement('div');
      header.style.cssText = `
        padding: 15px 20px; background: #f6f8fa; border-bottom: 1px solid #d0d7de;
        font-weight: bold; font-size: 16px; display: flex; justify-content: space-between; align-items: center;
      `;
      header.innerText = title;
  
      const closeBtn = document.createElement('button');
      closeBtn.innerText = '✕';
      closeBtn.style.cssText = `background: transparent; border: none; font-size: 16px; cursor: pointer; color: #57606a;`;
      closeBtn.onclick = () => overlay.remove();
      header.appendChild(closeBtn);
  
      const body = document.createElement('div');
      body.style.cssText = `padding: 20px; overflow-y: auto; flex-grow: 1;`;
  
      const textarea = document.createElement('textarea');
      textarea.value = textContent;
      textarea.style.cssText = `
        width: 100%; height: 250px; padding: 10px; border: 1px solid #d0d7de;
        border-radius: 6px; font-family: inherit; font-size: 14px; resize: vertical; box-sizing: border-box;
      `;
      body.appendChild(textarea);
  
      const footer = document.createElement('div');
      footer.style.cssText = `
        padding: 12px 20px; background: #f6f8fa; border-top: 1px solid #d0d7de;
        display: flex; justify-content: flex-end; gap: 10px;
      `;
  
      const copyBtn = document.createElement('button');
      copyBtn.innerText = '📋 Копировать в буфер';
      copyBtn.style.cssText = `
        background: #2ea44f; color: white; border: none; padding: 8px 16px;
        border-radius: 6px; font-weight: bold; cursor: pointer;
      `;
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(textarea.value).then(() => {
          copyBtn.innerText = '✅ Скопировано!';
          setTimeout(() => { copyBtn.innerText = '📋 Копировать в буфер'; }, 2000);
        });
      };
  
      const okBtn = document.createElement('button');
      okBtn.innerText = 'Закрыть';
      okBtn.style.cssText = `
        background: #f3f4f6; color: #24292f; border: 1px solid #d0d7de;
        padding: 8px 16px; border-radius: 6px; cursor: pointer;
      `;
      okBtn.onclick = () => overlay.remove();
  
      footer.appendChild(copyBtn);
      footer.appendChild(okBtn);
  
      modal.appendChild(header);
      modal.appendChild(body);
      modal.appendChild(footer);
      overlay.appendChild(modal);
      document.body.appendChild(overlay);
  
      overlay.onclick = (e) => {
        if (e.target === overlay) overlay.remove();
      };
    }
  
    function applyResponseToUI(data, mode) {
      if (data.task_name) {
        const taskNameInput = document.querySelector('input[name="task_name"]');
        if (taskNameInput) taskNameInput.value = data.task_name;
      }
  
      if (data.task_description) {
        const taskDescTextarea = document.querySelector('textarea[name="task_description"]');
        if (taskDescTextarea) taskDescTextarea.value = data.task_description;
      }
  
      if (data.task_time_minutes) {
        const taskTimeInput = document.querySelector('input#input-task_time');
        if (taskTimeInput) taskTimeInput.value = data.task_time_minutes;
      }
  
      if (data.task_executor) {
        const executorSelect = document.querySelector('select[name="task_executor"]');
        if (executorSelect) {
          Array.from(executorSelect.options).forEach((opt) => {
            if (opt.text.toLowerCase().includes(data.task_executor.toLowerCase()) || opt.value === data.task_executor) {
              executorSelect.value = opt.value;
            }
          });
        }
      }
  
      if (mode === 'reply_only' && data.email_reply_text) {
        showCopyModal('✉️ Черновик ответа клиенту', data.email_reply_text);
      } else if (mode === 'full_assistant') {
        let fullText = '';
        if (data.thread_summary) {
          fullText += `--- РЕВЬЮ ВСЕХ ЗАДАЧ И СТАТУСОВ ---\n${data.thread_summary}\n\n`;
        }
        if (data.email_reply_text) {
          fullText += `--- ЧЕРНОВИК ОТВЕТА ---\n${data.email_reply_text}`;
        }
        showCopyModal('🚀 Полный разбор ветки и задач', fullText.trim());
      }
    }
  
    function sendToBackend(mode, buttonEl) {
      const originalText = buttonEl.innerText;
      buttonEl.innerText = '⏳ Загрузка...';
      buttonEl.disabled = true;
  
      const payload = {
        mode: mode,
        context: parseCRMContext(),
        messages: parseVisibleMessages()
      };
  
      GM_xmlhttpRequest({
        method: 'POST',
        url: BACKEND_URL,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Secret': API_SECRET
        },
        data: JSON.stringify(payload),
        onload: function (response) {
          buttonEl.innerText = originalText;
          buttonEl.disabled = false;
  
          if (response.status === 200) {
            const result = JSON.parse(response.responseText);
            console.log('[AI Assistant] Response:', result);
            applyResponseToUI(result, mode);
          } else {
            console.error('[AI Assistant] Server Error:', response.responseText);
            alert('Ошибка бэкенда (' + response.status + '): ' + response.statusText);
          }
        },
        onerror: function (err) {
          buttonEl.innerText = originalText;
          buttonEl.disabled = false;
          console.error('[AI Assistant] Request Failed:', err);
          alert('Не удалось подключиться к бэкенду https://crm-ai-assistant.onrender.com');
        }
      });
    }
  
    function initUI() {
      if (document.getElementById('ai-assistant-panel')) return;
  
      const container = document.createElement('div');
      container.id = 'ai-assistant-panel';
      container.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 99999;
        background: #ffffff;
        border: 1px solid #d0d7de;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        display: flex;
        gap: 6px;
        font-family: Arial, sans-serif;
      `;
  
      const btnTask = document.createElement('button');
      btnTask.className = 'btn btn--light';
      btnTask.innerText = '✨ Сформировать задачу';
      btnTask.onclick = () => sendToBackend('task_only', btnTask);
  
      const btnReply = document.createElement('button');
      btnReply.className = 'btn btn--light';
      btnReply.innerText = '✉️ Черновик ответа';
      btnReply.onclick = () => sendToBackend('reply_only', btnReply);
  
      const btnFull = document.createElement('button');
      btnFull.className = 'btn';
      btnFull.innerText = '🚀 Полный разбор';
      btnFull.onclick = () => sendToBackend('full_assistant', btnFull);
  
      container.appendChild(btnTask);
      container.appendChild(btnReply);
      container.appendChild(btnFull);
      document.body.appendChild(container);
    }
  
    window.addEventListener('load', initUI);
  })();