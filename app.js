// 声明全局变量存储语言包
let en, zh, fr, es, de, ja, pt, ru, it, ar, ko, hi, id, tr, nl, pl, sv, vi, th, uk;

// 在DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    init();
});

// 初始化应用
async function init() {
    // 加载语言包
    en = await fetch('locales/en.json').then(res => res.json());
    zh = await fetch('locales/zh.json').then(res => res.json());
    fr = await fetch('locales/fr.json').then(res => res.json());
    es = await fetch('locales/es.json').then(res => res.json());
    de = await fetch('locales/de.json').then(res => res.json());
    ja = await fetch('locales/ja.json').then(res => res.json());
    pt = await fetch('locales/pt.json').then(res => res.json());
    ru = await fetch('locales/ru.json').then(res => res.json());
    it = await fetch('locales/it.json').then(res => res.json());
    ar = await fetch('locales/ar.json').then(res => res.json());
    ko = await fetch('locales/ko.json').then(res => res.json());
    hi = await fetch('locales/hi.json').then(res => res.json());
    id = await fetch('locales/id.json').then(res => res.json());
    tr = await fetch('locales/tr.json').then(res => res.json());
    nl = await fetch('locales/nl.json').then(res => res.json());
    pl = await fetch('locales/pl.json').then(res => res.json());
    sv = await fetch('locales/sv.json').then(res => res.json());
    vi = await fetch('locales/vi.json').then(res => res.json());
    th = await fetch('locales/th.json').then(res => res.json());
    uk = await fetch('locales/uk.json').then(res => res.json());
    
    // 初始化页面
    updateText();
    setupEventListeners();
    fetchAndDisplayIncome();
}

const supportedLanguages = ['zh', 'en', 'fr', 'es', 'de', 'ja', 'it', 'pt', 'ru', 'ar', 'ko', 'hi', 'id', 'tr', 'nl', 'pl', 'sv', 'vi', 'th', 'uk'];
const browserLang = navigator.language.split('-')[0];
let currentLang = supportedLanguages.includes(browserLang) ? browserLang : 'en';

// 更新页面文本
function updateText() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const keyPath = el.getAttribute('data-i18n').split('.');
        let translation;
        
        // 根据当前语言选择对应的翻译包
        switch(currentLang) {
            case 'zh':
                translation = zh;
                break;
            case 'fr':
                translation = fr;
                break;
            case 'es':
                translation = es;
                break;
            case 'de':
                translation = de;
                break;
            case 'ja':
                translation = ja;
                break;
            case 'pt':
                translation = pt;
                break;
            case 'ru':
                translation = ru;
                break;
            case 'it':
                translation = it;
                break;
            case 'ar':
                translation = ar;
                break;
            case 'ko':
                translation = ko;
                break;
            case 'hi':
                translation = hi;
                break;
            case 'id':
                translation = id;
                break;
            case 'tr':
                translation = tr;
                break;
            case 'nl':
                translation = nl;
                break;
            case 'pl':
                translation = pl;
                break;
            case 'sv':
                translation = sv;
                break;
            case 'vi':
                translation = vi;
                break;
            case 'th':
                translation = th;
                break;
            case 'uk':
                translation = uk;
                break;
            default:
                translation = en;
        }
        
        // 遍历键路径获取翻译值
        for (const key of keyPath) {
            if (translation && typeof translation === 'object' && key in translation) {
                translation = translation[key];
            } else {
                console.error(`Translation key not found: ${keyPath.join('.')}`);
                translation = `[[${keyPath.join('.')}]]`;
                break;
            }
        }
        
        if (typeof translation === 'string') {
            el.textContent = translation;
        }
    });
    // 设置HTML语言属性
    document.documentElement.lang = currentLang;
    // 设置RTL布局支持
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
}

// 获取并显示收入记录
async function fetchAndDisplayIncome() {
    try {
        const response = await fetch('/api/income');
        if (response.ok) {
            const data = await response.json();
            const tableBody = document.querySelector('#income-table tbody');
            tableBody.innerHTML = '';
            
            if (data.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="3" style="text-align:center;">${currentLang === 'zh' ? '暂无记录' : 'No records found'}</td></tr>`;
                return;
            }
            
            data.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td data-label="${getLocaleString('records.date')}">${record.date}</td>
                    <td data-label="${getLocaleString('records.amount')}">${record.amount}</td>
                    <td data-label="${getLocaleString('records.category')}">${record.category}</td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('success-message').textContent = 
            currentLang === 'zh' ? '加载记录失败' : 'Failed to load records';
    }
}

// 安全获取语言字符串的辅助函数
function getLocaleString(key) {
    const keys = key.split('.');
    const languageMap = { zh, en, fr, es, de, ja, it, pt, ru, ar, ko, hi, id, tr, nl, pl, sv, vi, th, uk };
    let result = languageMap[currentLang] || en;
    
    for (const k of keys) {
        if (result && typeof result === 'object' && k in result) {
            result = result[k];
        } else {
            console.error(`Translation key not found: ${key}`);
            return `[[${key}]]`;
        }
    }
    
    return typeof result === 'string' ? result : `[[${key}]]`;
}

// 添加深色模式切换功能
function setupEventListeners() {
    document.getElementById('lang-zh').addEventListener('click', () => {
        currentLang = 'zh';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-zh').classList.add('active');
    });

    document.getElementById('lang-en').addEventListener('click', () => {
        currentLang = 'en';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-en').classList.add('active');
    });

    document.getElementById('lang-fr').addEventListener('click', () => {
        currentLang = 'fr';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-fr').classList.add('active');
    });

    document.getElementById('lang-es').addEventListener('click', () => {
        currentLang = 'es';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-es').classList.add('active');
    });

    document.getElementById('lang-de').addEventListener('click', () => {
        currentLang = 'de';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-de').classList.add('active');
    });

    document.getElementById('lang-ja').addEventListener('click', () => {
        currentLang = 'ja';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-ja').classList.add('active');
    });

    document.getElementById('lang-it').addEventListener('click', () => {
        currentLang = 'it';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-it').classList.add('active');
    });

    document.getElementById('lang-pt').addEventListener('click', () => {
        currentLang = 'pt';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-pt').classList.add('active');
    });

    document.getElementById('lang-ru').addEventListener('click', () => {
        currentLang = 'ru';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-ru').classList.add('active');
    });

    document.getElementById('lang-ar').addEventListener('click', () => {
        currentLang = 'ar';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-ar').classList.add('active');
    });

    document.getElementById('lang-ko').addEventListener('click', () => {
        currentLang = 'ko';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-ko').classList.add('active');
    });

    document.getElementById('lang-hi').addEventListener('click', () => {
        currentLang = 'hi';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-hi').classList.add('active');
    });

    document.getElementById('lang-id').addEventListener('click', () => {
        currentLang = 'id';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-id').classList.add('active');
    });

    document.getElementById('lang-tr').addEventListener('click', () => {
        currentLang = 'tr';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-tr').classList.add('active');
    });

    document.getElementById('lang-nl').addEventListener('click', () => {
        currentLang = 'nl';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-nl').classList.add('active');
    });

    document.getElementById('lang-pl').addEventListener('click', () => {
        currentLang = 'pl';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-pl').classList.add('active');
    });

    document.getElementById('lang-sv').addEventListener('click', () => {
        currentLang = 'sv';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-sv').classList.add('active');
    });

    document.getElementById('lang-vi').addEventListener('click', () => {
        currentLang = 'vi';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-vi').classList.add('active');
    });

    document.getElementById('lang-th').addEventListener('click', () => {
        currentLang = 'th';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-th').classList.add('active');
    });

    document.getElementById('lang-uk').addEventListener('click', () => {
        currentLang = 'uk';
        updateText();
        fetchAndDisplayIncome();
        document.querySelector('.language-switcher button.active').classList.remove('active');
        document.getElementById('lang-uk').classList.add('active');
    });

    // 表单提交事件
    document.getElementById('income-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch('/api/income', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                document.getElementById('success-message').textContent = 
                    getLocaleString('success');
                e.target.reset();
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('success-message').textContent = 
                currentLang === 'zh' ? '保存失败，请重试。' : 'Save failed, please try again.';
        }
    });

    // 深色模式切换
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
    }
}
