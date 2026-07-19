
<!DOCTYPE html>
<html lang="am">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Shalom Technology</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
    body { background: #0b1219; min-height: 100vh; color: #fff; }
    .app-container { max-width: 420px; width: 100%; margin: 0 auto; min-height: 100vh; background: #17212b; overflow: hidden; padding: 14px; position: relative; }

    .header { text-align: center; padding-bottom: 12px; border-bottom: 1px solid #2b3a4a; margin-bottom: 12px; }
    .header .top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .header .lang-selector { display: flex; gap: 4px; }
    .header .lang-selector button { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); color: #8aa3b5; padding: 3px 8px; border-radius: 12px; font-size: 10px; cursor: pointer; }
    .header .lang-selector button.active { background: rgba(74,158,255,0.2); border-color: #4a9eff; color: #4a9eff; }
    .header .logo-img { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; box-shadow: 0 2px 10px rgba(0,0,0,0.4); animation: logoSpin 6s ease-in-out infinite; }
    .blink-slow { animation: blinkSlow 2.5s ease-in-out infinite; }
    @keyframes blinkSlow { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .phone-pulse { animation: phonePulse 1.4s ease-in-out infinite; display: inline-block; }
    @keyframes phonePulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.12); } }
    @keyframes logoSpin {
        0% { transform: rotateY(0deg) rotateX(0deg); }
        25% { transform: rotateY(360deg) rotateX(0deg); }
        50% { transform: rotateY(360deg) rotateX(360deg); }
        100% { transform: rotateY(360deg) rotateX(360deg); }
    }
    .menu-btn { transition: transform 0.2s ease; }
    .menu-btn:active { transform: scale(0.93); }
    .menu-btn .icon { transition: transform 0.3s ease; display: inline-block; }
    .menu-btn:hover .icon { transform: scale(1.2) rotate(8deg); }
    .promo-anim-card { animation: slideInFade 0.5s ease; }
    @keyframes slideInFade { from { opacity:0; transform: translateX(-15px); } to { opacity:1; transform: translateX(0); } }
    .product-card { animation: productRotateIn 0.6s ease; cursor: pointer; }
    @keyframes productRotateIn { from { opacity:0; transform: rotateY(15deg) scale(0.9); } to { opacity:1; transform: rotateY(0) scale(1); } }
    .fullscreen-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.92); z-index:999; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:20px; }
    .fullscreen-overlay img { max-width:100%; max-height:60%; border-radius:12px; }
    .fullscreen-overlay .close-fs { position:absolute; top:20px; right:20px; font-size:28px; color:#fff; cursor:pointer; }
    .header h1 { font-size: 18px; font-weight: 700; background: linear-gradient(90deg,#4a9eff,#7ac7ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 4px; }
    .header .sub { font-size: 11px; color: #8aa3b5; }

    .pages { padding: 6px 0 80px; }
    .page { display: none; animation: fadeSlide 0.25s ease; }
    .page.active { display: block; }
    @keyframes fadeSlide { 0% { opacity: 0; transform: translateY(10px); } 100% { opacity: 1; transform: translateY(0); } }
    .page-title { font-size: 15px; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 6px; margin-bottom: 10px; }
    .back-btn { background: rgba(255,255,255,0.08); border: none; color: #fff; font-size: 18px; padding: 2px 12px; border-radius: 30px; cursor: pointer; }

    .menu-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 12px; }
    .menu-btn { border-radius: 14px; padding: 10px 4px; text-align: center; font-size: 9px; font-weight: 500; cursor: pointer; color: #e0edf5; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .menu-btn .icon { font-size: 22px; display: block; margin-bottom: 2px; }
    .menu-btn:nth-child(1){background:linear-gradient(135deg,#2a3a4a,#1a2a3a);}
    .menu-btn:nth-child(2){background:linear-gradient(135deg,#4a2a22,#3a1a12);}
    .menu-btn:nth-child(3){background:linear-gradient(135deg,#4a3a1a,#3a2a0a);}
    .menu-btn:nth-child(4){background:linear-gradient(135deg,#1a4a3a,#0a3a2a);}
    .menu-btn:nth-child(5){background:linear-gradient(135deg,#3a2a5a,#2a1a4a);}
    .menu-btn:nth-child(6){background:linear-gradient(135deg,#4a2a3a,#3a1a2a);}
    .menu-btn:nth-child(7){background:linear-gradient(135deg,#4a3a1a,#3a2a0a);}
    .menu-btn:nth-child(8){background:linear-gradient(135deg,#1a4a3a,#0a3a2a);}
    .menu-btn:nth-child(9){background:linear-gradient(135deg,#2a3a5a,#1a2a4a);}
    .menu-btn:nth-child(10){background:linear-gradient(135deg,#1a4a3a,#0a3a2a);}
    .menu-btn:nth-child(11){background:linear-gradient(135deg,#4a2a1a,#3a1a0a);}
    .menu-btn:nth-child(12){background:linear-gradient(135deg,#2a4a4a,#1a3a3a);}
    .menu-btn:nth-child(13){background:linear-gradient(135deg,#4a4a1a,#3a3a0a);}
    .menu-btn:nth-child(14){background:linear-gradient(135deg,#4a2a2a,#3a1a1a);}
    .menu-btn:nth-child(15){background:linear-gradient(135deg,#1a2a4a,#0a1a3a);}
    .menu-btn:nth-child(16){background:linear-gradient(135deg,#3a2a5a,#2a1a4a);}
    .menu-btn:nth-child(17){background:linear-gradient(135deg,#4a2a3a,#3a1a2a);}

    .section-title { color: #b8a84a; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
    .product-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
    .product-card { background: rgba(255,255,255,0.04); border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 6px 18px rgba(0,0,0,0.25); transition: transform 0.2s ease; }
    .product-card:active { transform: scale(0.97); }
    .product-card .promo-img { width: 100%; height: 110px; object-fit: cover; background: linear-gradient(135deg,#1a2a3a,#2a3a4a); }
    .product-card .info { padding: 8px 10px; text-align: center; }
    .product-card .name { font-weight: 700; font-size: 12px; color: #d4c56a; }
    .product-card .desc { font-size: 9px; color: #8aa3b5; margin: 3px 0 6px; white-space: pre-line; max-height: 60px; overflow-y: auto; }
    .product-card .ask-btn { width: 100%; padding: 7px; border: none; border-radius: 10px; color: #fff; font-weight: 700; font-size: 10px; cursor: pointer; background: linear-gradient(135deg,#4a9eff,#2a7adf); box-shadow: 0 4px 12px rgba(74,158,255,0.3); }
    .channel-link { padding: 8px; background: rgba(74,158,255,0.08); border-radius: 12px; text-align: center; border: 1px dashed #4a9eff; margin-bottom: 10px; }
    .channel-link a { color: #4a9eff; font-weight: 600; text-decoration: none; font-size: 12px; }

    .promo-banner { background: linear-gradient(135deg,#4a2a2a,#3a1a1a); border-radius: 12px; padding: 10px 14px; margin-top: 10px; display: flex; align-items: center; gap: 10px; border: 1px solid #4a3a1a; }
    .promo-banner .text { font-size: 12px; color: #c0d8e8; flex: 1; font-weight: 600; }

    .bottom-nav-wrap { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); max-width: 420px; width: 100%; background: rgba(15,26,36,0.96); backdrop-filter: blur(14px); border-top: 1px solid #2b3a4a; padding: 8px 0 14px; overflow: hidden; }
    .bottom-nav { display: flex; width: max-content; animation: tickerScroll 14s linear infinite; }
    @keyframes tickerScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .nav-item { color: #6a8a9e; font-size: 8px; text-align: center; cursor: pointer; padding: 2px 6px; flex: 0 0 25%; box-sizing: border-box; }
    .nav-item.active { color: #4a9eff; }
    .nav-item .icon { font-size: 16px; display: block; }

    .btn-primary { background: #4a9eff; border: none; border-radius: 30px; padding: 10px; color: #fff; font-weight: 600; font-size: 13px; width: 100%; cursor: pointer; margin-top: 4px; }
    .btn-primary.gold { background: #b8a84a; color: #1a1a2e; }
    .shimmer-btn { position: relative; overflow: hidden; background: linear-gradient(135deg,#4a9eff,#2a7adf); color: #fff; font-size: 15px; font-weight: 700; padding: 14px 20px; border-radius: 40px; width: 100%; border: none; cursor: pointer; box-shadow: 0 8px 26px rgba(74,158,255,0.45); }
    .shimmer-btn:active { transform: scale(0.97); }
    .shimmer-btn::after { content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.25) 50%, transparent 60%); animation: shimmerMove 2.6s infinite; pointer-events:none; }
    @keyframes shimmerMove { 0% { transform: translateX(-100%) rotate(45deg); } 100% { transform: translateX(100%) rotate(45deg); } }
    .card-box { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 10px; border: 1px solid rgba(255,255,255,0.06); text-align: center; cursor: pointer; }
    .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
    .input-field { width:100%; padding:10px; margin-bottom:8px; background:rgba(255,255,255,0.05); border:1px solid #2b3a4a; border-radius:10px; color:#fff; font-size:13px; }
    .stat-box { background: rgba(255,255,255,0.04); border-radius: 8px; padding: 6px; text-align: center; }
    .stat-num { font-size: 16px; font-weight: 700; }
    .stat-label { font-size: 7px; color: #8aa3b5; }
    .empty-msg { text-align:center; opacity:0.6; margin-top: 30px; font-size: 12px; }
</style>
</head>
<body>

<div class="app-container">
    <div class="header">
        <div class="top-row">
            <img class="logo-img" src="/static/logo.jpg" />
            <div class="lang-selector" id="langSelector">
                <button class="active" data-lang="am" onclick="switchLanguage('am')">አማ</button>
                <button data-lang="en" onclick="switchLanguage('en')">EN</button>
                <button data-lang="ti" onclick="switchLanguage('ti')">ትግ</button>
                <button data-lang="or" onclick="switchLanguage('or')">ኦሮ</button>
            </div>
        </div>
        <h1 id="mainTitle">Shalom Technology</h1>
        <div class="sub" id="mainSub">✨ የእርስዎ የደህንነት አጋር ✨</div>
    </div>

    <div class="pages" id="pagesContainer">

        <!-- HOME -->
        <div class="page active" id="page-home">
            <div id="homeHeroBox" style="position:relative; overflow:hidden; background:linear-gradient(135deg,#1a2a3a,#243447); border-radius:22px; padding:28px 18px; text-align:center; border:1px solid rgba(74,158,255,0.15); box-shadow:0 8px 30px rgba(0,0,0,0.35);">
                <img id="homeHeroBg" src="" style="display:none; position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0.25; z-index:0;" />
                <div style="position:relative; z-index:1;">
                    <img src="/static/logo.jpg" style="width:84px; height:84px; border-radius:20px; object-fit:cover; box-shadow:0 8px 26px rgba(74,158,255,0.35); animation: logoSpin 6s ease-in-out infinite;" />
                    <div id="homeHeaderSlot" style="color:#fff; font-size:19px; font-weight:700; margin-top:12px;" class="blink-slow">Shalom Technology</div>
                    <div style="color:#9bb0c0; font-size:11px; margin-top:2px; letter-spacing:0.5px;">✨ የእርስዎ የደህንነት አጋር ✨</div>

                    <div style="background:rgba(255,255,255,0.04); border-radius:18px; padding:16px 14px; border:1px solid rgba(255,255,255,0.06); margin-top:18px;">
                        <div style="color:#fff; font-size:15px; font-weight:700; margin-bottom:6px;">Welcome!</div>
                        <div style="color:#fff; font-size:12px; line-height:1.9;">እንኳን ደህና መጡ! ✨</div>
                        <div style="color:#b8c8d8; font-size:12px; line-height:1.9;">እንኳዕ ደሓን መጻእኩም!</div>
                        <div style="color:#a0b8c8; font-size:12px; line-height:1.9;">Baga nagaan dhufte!</div>
                        <div style="width:60px; height:2px; background:linear-gradient(90deg,transparent,#4a9eff,transparent); margin:10px auto;"></div>
                        <div style="color:#b8c8d8; font-size:11px; line-height:1.6;">የእኛ ሙሉ አገልግሎት ለማየት ከታች ይጫኑ 👇</div>
                    </div>

                    <button class="shimmer-btn" style="margin-top:16px;" onclick="toggleHomeMenu()">🚀 እዚህ ይጫኑ / OPEN</button>
                    <div style="color:#6a8a9e; font-size:10px; margin-top:10px; display:flex; flex-wrap:wrap; justify-content:center; gap:4px 8px;">
                        <span>ለመክፈት እዚህ ጠቅ ያድርጉ</span><span>•</span><span>ንምክፋት ጠውቕ</span><span>•</span><span>Banuuf tuqi</span>
                    </div>
                </div>
            </div>
            <div id="homeMenuGrid" style="display:none; margin-top:12px;">
                <div class="menu-grid">
                    <div class="menu-btn" onclick="showPage('page-products')"><span class="icon">🛍️</span><span data-key="m1">ምርቶች</span></div>
                    <div class="menu-btn" onclick="showPage('page-call')"><span class="icon">📞</span><span data-key="m2">ይደውሉ</span></div>
                    <div class="menu-btn" onclick="showPage('page-social')"><span class="icon">🌐</span><span data-key="m3">ማህበራዊ</span></div>
                    <div class="menu-btn" onclick="showPage('page-share')"><span class="icon">👥</span><span data-key="m4">ማጋሪያ</span></div>
                    <div class="menu-btn" onclick="showPage('page-news')"><span class="icon">📰</span><span data-key="m5">ዜና</span></div>
                    <div class="menu-btn" onclick="showPage('page-applications')"><span class="icon">📱</span><span data-key="m6">Applications</span></div>
                    <div class="menu-btn" onclick="showPage('page-jobs')"><span class="icon">💼</span><span data-key="m7">ክፍት ስራ</span></div>
                    <div class="menu-btn" onclick="showPage('page-discount')"><span class="icon">🎁</span><span data-key="m8">ቅናሽ</span></div>
                    <div class="menu-btn" onclick="showPage('page-ai')"><span class="icon">🤖</span><span data-key="m9">ረዳት</span></div>
                    <div class="menu-btn" onclick="showPage('page-support')"><span class="icon">🛡️</span><span data-key="m10">ድጋፍ</span></div>
                    <div class="menu-btn" onclick="showPage('page-promo')"><span class="icon">📢</span><span data-key="m11">ማስታወቂያ</span></div>
                    <div class="menu-btn" onclick="showPage('page-tips')"><span class="icon">💡</span><span data-key="m12">ምክሮች</span></div>
                    <div class="menu-btn" onclick="showPage('page-banks')"><span class="icon">🏦</span><span data-key="m13">ባንክ</span></div>
                    <div class="menu-btn" onclick="showPage('page-feedback')"><span class="icon">💬</span><span data-key="m14">አስተያየት</span></div>
                    <div class="menu-btn" onclick="showPage('page-admin')"><span class="icon">⚙️</span><span data-key="m15">አድሚን</span></div>
                    <div class="menu-btn" onclick="showPage('page-teamleader')"><span class="icon">👔</span><span data-key="m16">ቲም ሊደር</span></div>
                    <div class="menu-btn" onclick="showPage('page-employee')"><span class="icon">👤</span><span data-key="m17">ሰራተኛ</span></div>
                </div>
            </div>
            <div class="promo-banner" onclick="showPage('page-promo')" style="cursor:pointer; margin-top:10px;">
                <span style="font-size:18px;">🔥</span>
                <span class="text" id="homePromoText">✨ ማስታወቂያ ለማየት እዚህ ይጫኑ</span>
            </div>
            <div style="margin-top:6px; text-align:center; color:#6a8a9e; font-size:9px;">
                📢 ቻናላችን: <a href="https://t.me/MarshalomTech" target="_blank" style="color:#4a9eff; text-decoration:none;">@MarshalomTech</a>
            </div>
        </div>

        <!-- PRODUCTS -->
        <div class="page" id="page-products">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button><span id="pTitle">🛍️ ምርቶች</span></div>
            <div class="product-grid" id="productGrid"><p class="empty-msg">⏳...</p></div>
            <div class="channel-link">📢 <a href="https://t.me/MarshalomTech" target="_blank" id="channelText">ተጨማሪ ምርቶች ለማየት ቻናላችንን ይቀላቀሉ</a> 📢</div>
        </div>

        <!-- CALL -->
        <div class="page" id="page-call">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>📞 <span id="callTitle">ይደውሉ</span></div>
            <div class="grid2" style="margin-top:6px;">
                <a href="tel:0931556590" class="card-box" style="text-decoration:none; color:inherit;">
                    <div style="font-size:14px; font-weight:700; color:#fff;">0931556590</div>
                    <div style="font-size:9px; color:#8aa3b5;" id="callLabel1">ኢትዮ ቴሌኮም</div>
                </a>
                <a href="tel:+251799556590" class="card-box" style="text-decoration:none; color:inherit;">
                    <div style="font-size:14px; font-weight:700; color:#fff;">+251799556590</div>
                    <div style="font-size:9px; color:#8aa3b5;" id="callLabel2">ሳፋሪኮም</div>
                </a>
                <a href="tel:+251967386958" class="card-box" style="text-decoration:none; color:inherit;">
                    <div style="font-size:14px; font-weight:700; color:#fff;">+251967386958</div>
                    <div style="font-size:9px; color:#8aa3b5;">ሳፋሪኮም</div>
                </a>
                <a href="https://wa.me/251799556590" target="_blank" class="card-box" style="text-decoration:none; color:inherit;">
                    <span style="font-size:20px; display:block;">💬</span>
                    <div style="font-size:9px; color:#8aa3b5;">WhatsApp</div>
                </a>
                <a href="https://t.me/MarshalomSupportBot" target="_blank" class="card-box" style="text-decoration:none; color:inherit;">
                    <span style="font-size:20px; display:block;">✈️</span>
                    <div style="font-size:9px; color:#8aa3b5;">Telegram</div>
                </a>
            </div>
            <div class="promo-banner" style="margin-top:10px;">
                <span style="font-size:18px;">📢</span>
                <span class="text">ማንኛውም ጊዜ ይደውሉልን — ደስተኞች ነን እርስዎን ለማገልገል!</span>
            </div>
        </div>

        <!-- SOCIAL -->
        <div class="page" id="page-social">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>🌐 <span id="socialTitle">ማህበራዊ</span></div>
            <div class="grid3" id="socialGrid" style="margin-top:6px;"></div>
            <div style="margin-top:10px; border-radius:12px; overflow:hidden;">
                <img src="/static/background.jpg" style="width:100%; height:120px; object-fit:cover; display:block;" />
            </div>
            <div class="channel-link" style="margin-top:8px;">🌐 <a href="https://marshalom.com" target="_blank">marshalom.com</a> 🌐</div>
        </div>

        <!-- SHARE -->
        <div class="page" id="page-share">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>👥 <span id="shareTitle">ማጋሪያ</span></div>
            <div style="border-radius:12px; overflow:hidden; margin-bottom:8px;">
                <img src="/static/product5.jpg" style="width:100%; height:110px; object-fit:cover; display:block;" />
            </div>
            <div style="background:rgba(74,158,255,0.04); border-radius:12px; padding:10px; border:1px solid rgba(74,158,255,0.06); font-size:11px; color:#c0d8e8; line-height:1.7; white-space:pre-line;" id="shareWelcomeBox">✨ እንኳን ደህና መጡ ወደ ማርሻሎም (Marshalom)! ✨
እኛ በኤሌክትሮኒክስ እና በደህንነት ካሜራዎች ላይ ጥራት ያለው አገልግሎት የምንሰጥ ታማኝ የቴክኖሎጂ አጋርዎ ነን። ✅
🚀 ዘመናዊ የደህንነት ካሜራዎች (CCTV) 📷 ጥራት ያላቸው ኤሌክትሮኒክስ እቃዎች 📺 ፈጣን እና አስተማማኝ አገልግሎት ⚡️
📢 ለወቅታዊ መረጃዎች እና ምርጥ ቅናሾች ቻናላችንን ይቀላቀሉ! https://t.me/MarshalomTech
🌐 ድር ጣቢያችንን ይጎብኙ፡ www.marshalom.com
🤖 ጥያቄ ካለዎት የኛን አውቶማቲክ ረዳት ያናግሩ፡ @MarshalomSupportBot
📞 ለበለጠ መረጃ ይደውሉልን፡ 0931556590</div>
            <button class="btn-primary" style="margin-top:10px;" onclick="shareChannel()" id="shareBtn">📤 ቻናላችንን ያጋሩ (Telegram ይምረጡ)</button>
            <div class="grid3" style="margin-top:8px;">
                <a id="shareWhatsapp" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">💬</span><span style="font-size:7px; color:#c0d8e8;">WhatsApp</span></a>
                <a id="shareFacebook" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">📘</span><span style="font-size:7px; color:#c0d8e8;">Facebook</span></a>
                <a id="shareTelegram" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">✈️</span><span style="font-size:7px; color:#c0d8e8;">Telegram</span></a>
                <a id="shareSMS" href="sms:?body=Check%20out%20Shalom%20Technology%3A%20https%3A%2F%2Ft.me%2FMarshalomTech" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">💬</span><span style="font-size:7px; color:#c0d8e8;">SMS</span></a>
                <a id="shareInstagram" href="https://instagram.com/marshalom" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">📸</span><span style="font-size:7px; color:#c0d8e8;">Instagram</span></a>
                <a id="shareTwitter" target="_blank" class="card-box" style="text-decoration:none; color:inherit;"><span style="font-size:18px; display:block;">🐦</span><span style="font-size:7px; color:#c0d8e8;">Twitter</span></a>
            </div>
        </div>

        <!-- NEWS -->
        <div class="page" id="page-news">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>📰 <span id="newsTitle">ዜና</span></div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-bottom:5px; border-left:3px solid #4a9eff;">
                <div style="color:#b8a84a; font-weight:600; font-size:11px;" id="news1_title">📸 አዲስ ካሜራ ፊት ብቻ ሳይሆን የእግር ንዝረትን ይለያል!</div>
                <div style="color:#c0d8e8; font-size:10px; margin-top:2px;" id="news1_desc">የቻይና ኩባንያ አዲስ AI ካሜራ አስገባ — ሰዎችን በእግራቸው እንቅስቃሴ ይለያል! 🦶</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-bottom:5px; border-left:3px solid #4a9eff;">
                <div style="color:#b8a84a; font-weight:600; font-size:11px;" id="news2_title">🚀 በአሜሪካ የሰማይ ላይ ካሜራ ተፈተሸ</div>
                <div style="color:#c0d8e8; font-size:10px; margin-top:2px;" id="news2_desc">ሰዎችን ከ5 ኪሎ ሜትር ርቀት የሚያውቅ ካሜራ ተፈተሸ! 🌍</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; border-left:3px solid #ff6b6b;">
                <div style="color:#ff6b6b; font-weight:600; font-size:11px;" id="news3_title">😂 አስቂኝ ዜና!</div>
                <div style="color:#c0d8e8; font-size:10px; margin-top:2px;" id="news3_desc">ማርሻሎም ለቦቱ ምስጢር ቁጥር "777" ደብቆታል! 🤫😂</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-top:5px; border-left:3px solid #ff6b6b;">
                <div style="color:#ff6b6b; font-weight:600; font-size:11px;">😂 አስቂኝ ዜና 2!</div>
                <div style="color:#c0d8e8; font-size:10px; margin-top:2px;">ካሜራ ገዝቶ የራሱን ውሻ ሌባ ብሎ ሪፖርት ያደረገ ደንበኛ! 🐶🚨</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px 10px; margin-top:5px; border-left:3px solid #ff6b6b;">
                <div style="color:#ff6b6b; font-weight:600; font-size:11px;">😂 አስቂኝ ዜና 3!</div>
                <div style="color:#c0d8e8; font-size:10px; margin-top:2px;">"ካሜራ ካለኝ ለምን ቁልፍ አስፈለገኝ?" ብሎ ቤቱን ሳይቆልፍ የወጣ ደንበኛ ታሪክ! 🔑😅</div>
            </div>
        </div>

        <!-- COMPARE -->
        <div class="page" id="page-applications">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>📱 <span id="applicationsTitle">Applications</span></div>
            <div id="applicationsGrid" class="product-grid"><p class="empty-msg">⏳...</p></div>
        </div>

        <!-- JOBS -->
        <div class="page" id="page-jobs">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>💼 <span id="jobsTitle">ክፍት ስራ</span></div>
            <div id="jobsList"><p class="empty-msg">⏳...</p></div>
        </div>

        <!-- DISCOUNT -->
        <div class="page" id="page-discount">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>🎁 <span id="discountTitle">ቅናሽ</span></div>
            <div id="discountBox" style="background:linear-gradient(135deg,#4a3a1a,#3a2a0a); border-radius:16px; padding:20px 12px; text-align:center; color:#b8a84a; border:1px solid #4a3a1a;">
                <div style="font-size:30px;">🎁</div>
                <div id="discountContent" style="font-size:13px; color:#c0d8e8; margin-top:6px;">⏳...</div>
            </div>
        </div>

        <!-- AI -->
        <div class="page" id="page-ai">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>🤖 <span id="aiTitle">ረዳት</span></div>
            <div id="aiChatWindow" style="background:rgba(0,0,0,0.15); border-radius:12px; padding:8px; height:340px; overflow-y:auto; margin-bottom:8px; display:flex; flex-direction:column; gap:6px;"></div>
            <div style="display:flex; gap:6px;">
                <input type="text" id="aiInput" placeholder="መልእክት ይጻፉ..." class="input-field" style="margin:0; flex:1;" onkeypress="if(event.key==='Enter') sendAIMessage()">
                <button class="btn-primary" style="width:60px; margin:0;" onclick="sendAIMessage()">➤</button>
            </div>
        </div>

        <!-- SUPPORT -->
        <div class="page" id="page-support">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>🛡️ <span id="supportTitle">ድጋፍ</span></div>
            <div style="text-align:center;">
                <div style="font-size:32px;">🛡️</div>
                <p style="color:#c0d8e8; font-size:13px; font-weight:600;" id="supportSub">24/7 ደንበኛ ድጋፍ</p>
                <div class="grid3" style="margin-top:6px;">
                    <a href="tel:0931556590" class="card-box" style="text-decoration:none; color:inherit;">
                        <span style="font-size:28px; display:block;">📞</span>
                        <span style="font-size:9px; color:#c0d8e8;">ስልክ</span>
                        <span style="font-size:8px; color:#8aa3b5;">0931556590</span>
                    </a>
                    <a href="https://wa.me/251799556590" target="_blank" class="card-box" style="text-decoration:none; color:inherit;">
                        <span style="font-size:28px; display:block;">💬</span>
                        <span style="font-size:9px; color:#c0d8e8;">ዋትሳፕ</span>
                        <span style="font-size:8px; color:#8aa3b5;">+251799556590</span>
                    </a>
                    <a href="https://t.me/MarshalomTech" target="_blank" class="card-box" style="text-decoration:none; color:inherit;">
                        <span style="font-size:28px; display:block;">✈️</span>
                        <span style="font-size:9px; color:#c0d8e8;">ቴሌግራም</span>
                        <span style="font-size:8px; color:#8aa3b5;">@MarshalomTech</span>
                    </a>
                </div>
                <a href="tel:0931556590" style="text-decoration:none;"><button class="btn-primary" style="margin-top:6px;" id="supportBtn">📞 ወዲያው ይደውሉ</button></a>
            </div>
        </div>

        <!-- PROMO -->
        <div class="page" id="page-promo">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>📢 <span id="promoTitle">ማስታወቂያ</span></div>
            <div id="promoList"><p class="empty-msg">⏳...</p></div>
        </div>

        <!-- TIPS -->
        <div class="page" id="page-tips">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>💡 <span id="tipsTitle">ምክሮች</span></div>
            <div style="border-radius:12px; overflow:hidden; margin-bottom:8px;">
                <img src="/static/product3.jpg" style="width:100%; height:100px; object-fit:cover; display:block;" />
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:4px;">
                <div style="color:#b8a84a; font-size:11px;" id="tip1">💡 ምክር 1</div>
                <div style="color:#c0d8e8; font-size:11px;" id="tip1d">ካሜራ ሲጭኑ የፀሐይ ብርሃን ወደሚያገኝ ቦታ ይጫኑ!</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:4px;">
                <div style="color:#b8a84a; font-size:11px;" id="tip2">💡 ምክር 2</div>
                <div style="color:#c0d8e8; font-size:11px;" id="tip2d">የካሜራ ስርዓትን በየጊዜው ያሻሽሉ!</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px;">
                <div style="color:#b8a84a; font-size:11px;">💡 ምክር 3</div>
                <div style="color:#c0d8e8; font-size:11px;">ካሜራዎ በ 4G/Wi-Fi ሲገናኝ የይለፍ ቃል ጠንካራ ያድርጉ!</div>
            </div>
        </div>

        <!-- BANKS -->
        <div class="page" id="page-banks">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>🏦 <span id="banksTitle">ባንክ</span></div>
            <div id="banksList"><p class="empty-msg">⏳...</p></div>
        </div>

        <!-- LOGIN -->
        <div class="page" id="page-feedback">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>💬 <span id="feedbackTitle">አስተያየት እና ምስክርነት</span></div>

            <div style="background:rgba(255,255,255,0.03); border-radius:12px; padding:10px; margin-bottom:10px;">
                <div style="color:#b8a84a; font-size:12px; font-weight:600; margin-bottom:6px;">✍️ የእርስዎን አስተያየት ይላኩ (ለሁሉም ይታያል)</div>
                <textarea id="testimonialInput" class="input-field" rows="2" placeholder="ስለ አገልግሎታችን ምን ይላሉ?"></textarea>
                <button class="btn-primary" onclick="submitTestimonial()">📤 ላክ</button>
            </div>

            <div style="background:rgba(74,158,255,0.04); border-radius:12px; padding:10px; margin-bottom:10px; border:1px solid rgba(74,158,255,0.08);">
                <div style="color:#4a9eff; font-size:12px; font-weight:600; margin-bottom:6px;">📩 ወደ አድሚን/ቲም ሊደር የግል መልእክት</div>
                <textarea id="privateMessageInput" class="input-field" rows="2" placeholder="መልእክትዎን ይጻፉ..."></textarea>
                <button class="btn-primary gold" onclick="submitPrivateMessage()">📤 ላክ (ወደ አድሚን)</button>
            </div>

            <div class="section-title">🌟 የደንበኞቻችን ምስክርነት</div>
            <div id="testimonialsList"><p class="empty-msg">⏳...</p></div>
        </div>

        <!-- ADMIN -->
        <div class="page" id="page-admin">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>⚙️ <span id="adminTitle">አድሚን</span></div>
            <div id="adminContent"><p class="empty-msg">⏳ በማረጋገጥ ላይ...</p></div>
        </div>

        <!-- TEAM LEADER -->
        <div class="page" id="page-teamleader">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>👔 <span id="tlTitle">ቲም ሊደር</span></div>
            <div id="tlLoginBox">
                <input type="text" id="tlUsername" placeholder="Username" class="input-field">
                <input type="password" id="tlPassword" placeholder="Password" class="input-field">
                <button class="btn-primary" onclick="teamLeaderLogin()">🔓 ግባ</button>
                <div id="tlMsg" style="font-size:11px; text-align:center; margin-top:6px; color:#ff6b6b;"></div>
            </div>
            <div id="tlContent" style="display:none;"></div>
        </div>

        <!-- EMPLOYEE -->
        <div class="page" id="page-employee">
            <div class="page-title"><button class="back-btn" onclick="showPage('page-home')">‹</button>👤 <span id="empTitle">ሰራተኛ</span></div>
            <div id="empLoginBox">
                <input type="text" id="empUsername" placeholder="Username" class="input-field">
                <input type="password" id="empPassword" placeholder="Password" class="input-field">
                <button class="btn-primary" onclick="employeeLogin()">🔓 ግባ</button>
                <div id="empMsg" style="font-size:11px; text-align:center; margin-top:6px; color:#ff6b6b;"></div>
            </div>
            <div id="empContent" style="display:none;"></div>
        </div>

    </div>

    <button id="bigBackBtn" onclick="showPage('page-home')" style="display:none; position:fixed; bottom:78px; left:50%; transform:translateX(-50%); max-width:380px; width:calc(100% - 28px); background:#4a9eff; color:#fff; font-size:14px; font-weight:700; padding:12px; border:none; border-radius:14px; box-shadow:0 6px 20px rgba(74,158,255,0.4); z-index:50;">🏠⬅️ ተመለስ / BACK</button>

    <div class="bottom-nav-wrap">
        <div class="bottom-nav" id="bottomNavTicker">
            <div class="nav-item active" onclick="showPage('page-home')"><span class="icon">🏠</span><span data-key="n1">መነሻ</span></div>
            <div class="nav-item" onclick="showPage('page-products')"><span class="icon">🛍️</span><span data-key="n2">ምርቶች</span></div>
            <div class="nav-item" onclick="showPage('page-ai')"><span class="icon">🤖</span><span data-key="n3">ረዳት</span></div>
            <div class="nav-item" onclick="showPage('page-share')"><span class="icon">👥</span><span data-key="n4">አጋራ</span></div>
            <div class="nav-item" onclick="showPage('page-jobs')"><span class="icon">💼</span><span data-key="n5">ስራ</span></div>
            <div class="nav-item" onclick="showPage('page-home')"><span class="icon">🏠</span><span data-key="n1">መነሻ</span></div>
            <div class="nav-item" onclick="showPage('page-products')"><span class="icon">🛍️</span><span data-key="n2">ምርቶች</span></div>
            <div class="nav-item" onclick="showPage('page-ai')"><span class="icon">🤖</span><span data-key="n3">ረዳት</span></div>
            <div class="nav-item" onclick="showPage('page-share')"><span class="icon">👥</span><span data-key="n4">አጋራ</span></div>
            <div class="nav-item" onclick="showPage('page-jobs')"><span class="icon">💼</span><span data-key="n5">ስራ</span></div>
        </div>
    </div>
</div>

<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
const initData = tg.initData;
const tgUser = (tg.initDataUnsafe && tg.initDataUnsafe.user) ? tg.initDataUnsafe.user : {};

let currentLang = 'am';
let allProducts = [];
let teamLeaderCreds = null;

const translations = {
    am: {
        title:'Shalom Technology', sub:'✨ የእርስዎ የደህንነት አጋር ✨',
        m1:'ምርቶች',m2:'ይደውሉ',m3:'ማህበራዊ',m4:'ማጋሪያ',m5:'ዜና',m6:'ንጽጽር',m7:'ክፍት ስራ',m8:'ቅናሽ',
        m9:'ረዳት',m10:'ድጋፍ',m11:'ማስታወቂያ',m12:'ምክሮች',m13:'ባንክ',m14:'መግቢያ',m15:'አድሚን',m16:'ቲም ሊደር',m17:'ሰራተኛ',
        n1:'መነሻ',n2:'ምርቶች',n3:'ረዳት',n4:'አጋራ',n5:'ስራ',
        pTitle:'🛍️ ምርቶች', channelText:'ተጨማሪ ምርቶች ለማየት ቻናላችንን ይቀላቀሉ',
        callTitle:'ይደውሉ', callLabel1:'ኢትዮ ቴሌኮም', callLabel2:'ሳፋሪኮም',
        socialTitle:'ማህበራዊ', shareTitle:'ማጋሪያ',
        shareWelcomeTitle:'✨ እንኳን ደህና መጡ ወደ Shalom Technology! ✨', shareWelcomeText:'ይህንን ቦት ለጓደኞችዎ ያጋሩ!',
        shareBtn:'📤 ቻናላችንን ያጋሩ (Telegram ይምረጡ)',
        newsTitle:'ዜና', applicationsTitle:'Applications', feedbackTitle:'አስተያየት እና ምስክርነት',
        jobsTitle:'ክፍት ስራ', jobsApply:'📝 አሁን አመልክት', jobsEmpty:'ለጊዜው ክፍት የስራ ቦታ የለም',
        discountTitle:'ቅናሽ', aiTitle:'ረዳት', supportTitle:'ድጋፍ', supportSub:'24/7 ደንበኛ ድጋፍ',
        promoTitle:'ማስታወቂያ', promoEmpty:'ለጊዜው ማስታወቂያ የለም',
        tipsTitle:'ምክሮች', banksTitle:'ባንክ',
        loginTitle:'መግቢያ', loginSub:'ለቲም ሊደር እና ሰራተኞች (ባለቤት ራሱ በራስ-ሰር ይታወቃል)', loginBtn:'🔓 ግባ',
        adminTitle:'አድሚን', tlTitle:'ቲም ሊደር', empTitle:'ሰራተኛ',
        askPrice:'💬 ዋጋ ጠይቁ', askSent:'✅ ጥያቄዎ ተልኳል!',
        phonePlaceholder:'ስልክ ቁጥርዎን ያስገቡ', applyBtn:'📝 አመልክት', applySent:'✅ ማመልከቻዎ ተልኳል!',
        wrongLogin:'❌ የተሳሳተ username ወይም password', mustChangePw:'🔐 መጀመሪያ password ይቀይሩ:',
        setPwBtn:'✅ Password ቀይር', pwChanged:'✅ Password ተቀይሯል!'
    },
    en: {
        title:'Shalom Technology', sub:'✨ Your Security Partner ✨',
        m1:'Products',m2:'Call',m3:'Social',m4:'Share',m5:'News',m6:'Compare',m7:'Jobs',m8:'Discount',
        m9:'Assistant',m10:'Support',m11:'Promo',m12:'Tips',m13:'Banks',m14:'Login',m15:'Admin',m16:'Team Leader',m17:'Employee',
        n1:'Home',n2:'Products',n3:'Assistant',n4:'Share',n5:'Jobs',
        pTitle:'🛍️ Products', channelText:'Join our channel for more products',
        callTitle:'Call', callLabel1:'Ethio Telecom', callLabel2:'Safaricom',
        socialTitle:'Social', shareTitle:'Share',
        shareWelcomeTitle:'✨ Welcome to Shalom Technology! ✨', shareWelcomeText:'Share this bot with your friends!',
        shareBtn:'📤 Share our channel (choose Telegram)',
        newsTitle:'News', applicationsTitle:'Applications', feedbackTitle:'Feedback & Testimonials',
        jobsTitle:'Jobs', jobsApply:'📝 Apply Now', jobsEmpty:'No open positions right now',
        discountTitle:'Discount', aiTitle:'Assistant', supportTitle:'Support', supportSub:'24/7 Customer Support',
        promoTitle:'Promo', promoEmpty:'No promotions right now',
        tipsTitle:'Tips', banksTitle:'Banks',
        loginTitle:'Login', loginSub:'For Team Leader & Employees (Owner is auto-detected)', loginBtn:'🔓 Login',
        adminTitle:'Admin', tlTitle:'Team Leader', empTitle:'Employee',
        askPrice:'💬 Ask Price', askSent:'✅ Request sent!',
        phonePlaceholder:'Enter your phone number', applyBtn:'📝 Apply', applySent:'✅ Application sent!',
        wrongLogin:'❌ Wrong username or password', mustChangePw:'🔐 Please set a new password first:',
        setPwBtn:'✅ Change Password', pwChanged:'✅ Password changed!'
    },
    ti: {
        title:'Shalom Technology', sub:'✨ ናይ ሓልዎት ኣጋርኩም ✨',
        m1:'ምርቶች',m2:'ደውሉ',m3:'ማህበራዊ',m4:'ኣጋሩ',m5:'ዜና',m6:'ንጽጽር',m7:'ስራ',m8:'ቅናሽ',
        m9:'ረዳት',m10:'ድጋፍ',m11:'ማስታወቂያ',m12:'ምኽርታት',m13:'ባንክ',m14:'ምእታው',m15:'ኣድሚን',m16:'መራሒ ጉጅለ',m17:'ሰራተኛ',
        n1:'መነሻ',n2:'ምርቶች',n3:'ረዳት',n4:'ኣጋሩ',n5:'ስራ',
        pTitle:'🛍️ ምርቶች', channelText:'ካልኦት ምርትታት ንምርኣይ ቻናልና ተጸንበሩ',
        callTitle:'ደውሉ', callLabel1:'ኢትዮ ተለኮም', callLabel2:'ሳፋሪኮም',
        socialTitle:'ማህበራዊ', shareTitle:'ኣጋሩ',
        shareWelcomeTitle:'✨ ናብ Shalom Technology ብደሓን መጻእኩም! ✨', shareWelcomeText:'ነዚ ቦት ንመሓዙትኩም ኣጋሩ!',
        shareBtn:'📤 ቻናልና ኣጋሩ',
        newsTitle:'ዜና', applicationsTitle:'Applications', feedbackTitle:'ርእይቶን ምስክርነትን',
        jobsTitle:'ክፍቲ ስራሕ', jobsApply:'📝 ሕጂ ኣመልክቱ', jobsEmpty:'ሕጂ ክፍቲ ቦታ የለን',
        discountTitle:'ቅናሽ', aiTitle:'ረዳት', supportTitle:'ደገፍ', supportSub:'24/7 ደገፍ ዓሚል',
        promoTitle:'ማስታወቂያ', promoEmpty:'ሕጂ ማስታወቂያ የለን',
        tipsTitle:'ምኽርታት', banksTitle:'ባንክ',
        loginTitle:'ምእታው', loginSub:'ንመራሒ ጉጅለን ሰራተኛታትን', loginBtn:'🔓 እቶ',
        adminTitle:'ኣድሚን', tlTitle:'መራሒ ጉጅለ', empTitle:'ሰራተኛ',
        askPrice:'💬 ዋጋ ሕተት', askSent:'✅ ተላኢኹ!',
        phonePlaceholder:'ቁጽሪ ስልኪ ኣእትዉ', applyBtn:'📝 ኣመልክት', applySent:'✅ ማመልከቻ ተላኢኹ!',
        wrongLogin:'❌ ግጉይ username ወይ password', mustChangePw:'🔐 መጀመርታ password ቀይሩ:',
        setPwBtn:'✅ Password ቀይር', pwChanged:'✅ ተቐይሩ!'
    },
    or: {
        title:'Shalom Technology', sub:'✨ Michuu Nageenya Keessanii ✨',
        m1:'Oomishaalee',m2:'Bilbilaa',m3:'Hawaasa',m4:'Qooda',m5:'Oduu',m6:'Madaalii',m7:'Hojii',m8:'Hir’aa',
        m9:'Gargaaraa',m10:'Deggersa',m11:'Beeksisa',m12:'Gorsa',m13:'Baankii',m14:'Seensa',m15:'Admin',m16:'Hoogganaa',m17:'Hojjetaa',
        n1:'Mana',n2:'Oomishaalee',n3:'Gargaaraa',n4:'Qooda',n5:'Hojii',
        pTitle:'🛍️ Oomishaalee', channelText:'Oomisha dabalataaf channel keenya hordofaa',
        callTitle:'Bilbilaa', callLabel1:'Ethio Telecom', callLabel2:'Safaricom',
        socialTitle:'Hawaasa', shareTitle:'Qooda',
        shareWelcomeTitle:'✨ Baga Nagaan Dhuftan Shalom Technology! ✨', shareWelcomeText:'Bot kana hiriyoota keessaniif qoodaa!',
        shareBtn:'📤 Channel keenya qoodaa',
        newsTitle:'Oduu', applicationsTitle:'Applications', feedbackTitle:'Yaada fi Ragaa',
        jobsTitle:'Hojii Banaa', jobsApply:'📝 Amma Iyyadhu', jobsEmpty:'Yeroo ammaa hojiin banaan hin jiru',
        discountTitle:'Hir’aa', aiTitle:'Gargaaraa', supportTitle:'Deggersa', supportSub:'Deggersa Maamilaa 24/7',
        promoTitle:'Beeksisa', promoEmpty:'Yeroo ammaa beeksisni hin jiru',
        tipsTitle:'Gorsa', banksTitle:'Baankii',
        loginTitle:'Seensa', loginSub:'Hoogganaa fi Hojjettootaaf', loginBtn:'🔓 Seeni',
        adminTitle:'Admin', tlTitle:'Hoogganaa', empTitle:'Hojjetaa',
        askPrice:'💬 Gaafii Gatii', askSent:'✅ Ergameera!',
        phonePlaceholder:'Lakkoofsa bilbila keessan galchaa', applyBtn:'📝 Iyyadhu', applySent:'✅ Iyyannoon ergameera!',
        wrongLogin:'❌ username ykn password dogongora', mustChangePw:'🔐 Duraan dursanii password haaraa qopheessaa:',
        setPwBtn:'✅ Password Jijjiiri', pwChanged:'✅ Jijjiirameera!'
    }
};

function setText(id, value) {
    const el = document.getElementById(id);
    if (el && value !== undefined) el.textContent = value;
}
function switchLanguage(lang) {
    currentLang = lang;
    const t = translations[lang];
    document.querySelectorAll('.lang-selector button').forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
    setText('mainTitle', t.title);
    setText('mainSub', t.sub);
    document.querySelectorAll('[data-key]').forEach(el => {
        const key = el.dataset.key;
        if (t[key]) el.textContent = t[key];
    });
    setText('pTitle', t.pTitle);
    setText('channelText', t.channelText);
    setText('callTitle', t.callTitle);
    setText('callLabel1', t.callLabel1);
    setText('callLabel2', t.callLabel2);
    setText('socialTitle', t.socialTitle);
    setText('shareTitle', t.shareTitle);
    setText('shareWelcomeTitle', t.shareWelcomeTitle);
    setText('shareWelcomeText', t.shareWelcomeText);
    setText('shareBtn', t.shareBtn);
    setText('newsTitle', t.newsTitle);
    setText('applicationsTitle', t.applicationsTitle || 'Applications');
    setText('jobsTitle', t.jobsTitle);
    setText('discountTitle', t.discountTitle);
    setText('aiTitle', t.aiTitle);
    setText('supportTitle', t.supportTitle);
    setText('supportSub', t.supportSub);
    setText('promoTitle', t.promoTitle);
    setText('tipsTitle', t.tipsTitle);
    setText('banksTitle', t.banksTitle);
    setText('feedbackTitle', t.feedbackTitle || 'አስተያየት እና ምስክርነት');
    setText('adminTitle', t.adminTitle);
    setText('tlTitle', t.tlTitle);
    setText('empTitle', t.empTitle);
    renderProducts();
    renderPromos();
    renderJobs();
    loadApplications();
    loadTestimonials();
    loadSocial();
}

function toggleHomeMenu() {
    const grid = document.getElementById('homeMenuGrid');
    grid.style.display = grid.style.display === 'none' ? 'block' : 'none';
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(pageId);
    if (target) target.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    if (pageId === 'page-home') document.querySelector('.nav-item:nth-child(1)').classList.add('active');
    else if (pageId === 'page-products') document.querySelector('.nav-item:nth-child(2)').classList.add('active');
    else if (pageId === 'page-ai') document.querySelector('.nav-item:nth-child(3)').classList.add('active');
    else if (pageId === 'page-share') document.querySelector('.nav-item:nth-child(4)').classList.add('active');
    else if (pageId === 'page-jobs') document.querySelector('.nav-item:nth-child(5)').classList.add('active');
    document.getElementById('bigBackBtn').style.display = (pageId === 'page-home') ? 'none' : 'block';
    if (pageId === 'page-admin') loadAdminPage();
}

// ===== PRODUCTS =====
async function loadProducts() {
    const res = await fetch('/api/products');
    allProducts = await res.json();
    renderProducts();
}
function renderProducts() {
    const t = translations[currentLang];
    const el = document.getElementById('productGrid');
    if (!allProducts.length) { el.innerHTML = '<p class="empty-msg">...</p>'; return; }
    el.innerHTML = allProducts.map((p, idx) => `
        <div class="product-card" style="animation-delay:${idx * 0.08}s;">
            <img class="promo-img" src="${p.photo_url || '/static/logo.jpg'}" onclick='openFullscreen(${JSON.stringify(p.photo_url || "/static/logo.jpg")}, ${JSON.stringify(p.name)})' />
            <div class="info">
                <div class="name">${p.name}</div>
                <div class="desc">${p.description || ''}</div>
                <button class="ask-btn" onclick='askPrice(${p.id}, ${JSON.stringify(p.name)})'>${t.askPrice}</button>
            </div>
        </div>
    `).join('');
}
function openFullscreen(photoUrl, name) {
    const overlay = document.createElement('div');
    overlay.className = 'fullscreen-overlay';
    overlay.innerHTML = `<span class="close-fs" onclick="this.parentElement.remove()">✕</span><img src="${photoUrl}"/><div style="color:#fff; margin-top:12px; font-size:14px; font-weight:600;">${name}</div>`;
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    document.body.appendChild(overlay);
}
// Rotate product display order every 8 hours (client-side, while catalog stays open across sessions)
function maybeRotateProducts() {
    const lastRotate = parseInt(localStorage_fallback('lastProductRotate') || '0');
    const now = Date.now();
    if (now - lastRotate > 8 * 60 * 60 * 1000 && allProducts.length > 1) {
        allProducts.push(allProducts.shift());
        renderProducts();
    }
}
let _memoryStore = {};
function localStorage_fallback(key, value) {
    if (value !== undefined) { _memoryStore[key] = value; return; }
    return _memoryStore[key];
}
async function askPrice(productId, productName) {
    const t = translations[currentLang];
    await fetch('/api/ask_price', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({initData, product_id: productId, product_name: productName})
    });
    alert(t.askSent);
}

// ===== JOBS =====
async function loadJobs() {
    const res = await fetch('/api/jobs');
    window._jobs = await res.json();
    renderJobs();
}
function renderJobs() {
    const t = translations[currentLang];
    const el = document.getElementById('jobsList');
    const jobs = window._jobs || [];
    if (!jobs.length) { el.innerHTML = `<p class="empty-msg">${t.jobsEmpty}</p>`; return; }
    el.innerHTML = jobs.map(j => `
        <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:6px; border-left:4px solid #4a9eff;">
            <h3 style="color:#fff; font-size:12px;">${j.title}</h3>
            <p style="color:#9bb0c0; font-size:10px;">${j.location || ''}</p>
            <p style="color:#c0d8e8; font-size:10px; margin-top:4px;">${j.description || ''}</p>
            ${j.pdf_url ? `<a href="${j.pdf_url}" download="job_details.pdf" class="ask-btn" style="display:block; text-decoration:none; box-sizing:border-box; margin-top:6px;">📄 ዝርዝር PDF አውርድ</a>` : ''}
            <input type="text" id="phone-${j.id}" placeholder="${t.phonePlaceholder}" class="input-field" style="margin-top:6px;">
            <input type="email" id="email-${j.id}" placeholder="Gmail / Email" class="input-field">
            <input type="text" id="idnum-${j.id}" placeholder="የመታወቂያ ቁጥር (ID Number)" class="input-field">
            <div style="font-size:9px; color:#8aa3b5; margin-bottom:4px;">📸 ሰልፊ ፎቶ (አማራጭ)</div>
            <input type="file" id="selfie-${j.id}" accept="image/*" class="input-field" style="padding:6px;">
            <button class="btn-primary" onclick="applyJob(${j.id}, ${JSON.stringify(j.title)})">${t.applyBtn}</button>
        </div>
    `).join('');
}
async function applyJob(jobId, jobTitle) {
    const t = translations[currentLang];
    const phone = document.getElementById('phone-' + jobId).value;
    const email = document.getElementById('email-' + jobId).value;
    const id_number = document.getElementById('idnum-' + jobId).value;
    const selfieInput = document.getElementById('selfie-' + jobId);
    let selfie_photo = null;
    if (selfieInput.files && selfieInput.files[0]) {
        selfie_photo = await fileToBase64(selfieInput.files[0]);
    }
    await fetch('/api/jobs/apply', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({initData, job_id: jobId, job_title: jobTitle, phone, email, id_number, selfie_photo})
    });
    alert(t.applySent);
}

// ===== PROMOS =====
async function loadPromos() {
    const res = await fetch('/api/promos');
    window._promos = await res.json();
    renderPromos();
    renderDiscount();
}
function renderPromos() {
    const t = translations[currentLang];
    const el = document.getElementById('promoList');
    const promos = (window._promos || []).slice(0, 3);
    if (!promos.length) { el.innerHTML = `<p class="empty-msg">${t.promoEmpty}</p>`; return; }
    const promoPhotos = ['/static/product1.jpg', '/static/product3.jpg', '/static/product5.jpg'];
    el.innerHTML = promos.map((p, i) => `
        <div class="promo-anim-card" style="display:flex; gap:8px; align-items:center; background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; border-left:4px solid #4a9eff; margin-bottom:6px;">
            <div style="flex:1; color:#c0d8e8; font-size:11px;">${p[currentLang] || p.am}</div>
            <img src="${promoPhotos[i % promoPhotos.length]}" style="width:60px; height:60px; border-radius:8px; object-fit:cover; flex-shrink:0;" />
        </div>
    `).join('');
    const homeText = document.getElementById('homePromoText');
    if (promos.length && homeText) homeText.textContent = (promos[0][currentLang] || promos[0].am);
}
function renderDiscount() {
    const promos = window._promos || [];
    const el = document.getElementById('discountContent');
    if (promos.length) {
        el.textContent = promos[0][currentLang] || promos[0].am;
    } else {
        el.textContent = currentLang === 'en' ? 'No active discount right now' : 'ለጊዜው ንቁ ቅናሽ የለም';
    }
}

// ===== BANKS =====
const DEFAULT_SOCIAL = [
    {icon: '🎵', name: 'TikTok', url: 'https://tiktok.com/@marshalomcctv'},
    {icon: '▶️', name: 'YouTube', url: 'https://youtube.com/@ShalomTechnology'},
    {icon: '📘', name: 'Facebook', url: 'https://facebook.com/share/1YEeCpFBgp'},
    {icon: '📸', name: 'Instagram', url: 'https://instagram.com/marshalom'},
    {icon: '🐦', name: 'Twitter/X', url: 'https://twitter.com/marshalom'},
    {icon: '💼', name: 'LinkedIn', url: 'https://linkedin.com/company/marshalom'}
];
async function loadHomeSettings() {
    const res = await fetch('/api/config/home_settings');
    const settings = await res.json();
    const headerMode = (settings && settings.header_mode) || 'text';
    const bgPhotos = (settings && settings.bg_photos) || [];

    const slot = document.getElementById('homeHeaderSlot');
    if (headerMode === 'phone') {
        slot.className = 'phone-pulse';
        slot.innerHTML = '📞 <a href="tel:0931556590" style="color:#4a9eff; text-decoration:none;">0931556590</a>';
    } else {
        slot.className = 'blink-slow';
        slot.textContent = 'Shalom Technology';
    }

    const bgImg = document.getElementById('homeHeroBg');
    if (bgPhotos.length) {
        let idx = 0;
        bgImg.style.display = 'block';
        bgImg.src = bgPhotos[0];
        if (bgPhotos.length > 1) {
            setInterval(() => {
                idx = (idx + 1) % bgPhotos.length;
                bgImg.src = bgPhotos[idx];
            }, 8000);
        }
    }
}

async function loadSocial() {
    const res = await fetch('/api/config/social');
    let links = await res.json();
    if (!links || !links.length) links = DEFAULT_SOCIAL;
    document.getElementById('socialGrid').innerHTML = links.map(s => `
        <a href="${s.url}" target="_blank" class="card-box" style="text-decoration:none; color:inherit;">
            <span style="font-size:24px; display:block;">${s.icon}</span>
            <span style="font-size:8px; color:#c0d8e8;">${s.name}</span>
        </a>
    `).join('');
}

const DEFAULT_BANKS = [
    {bank: 'የንግድ ባንክ', number: '1000453578058', owner: 'Marshalom Tesfay'},
    {bank: 'ቴሌብር 1', number: '0931556590', owner: 'Marshalom Tesfay'},
    {bank: 'ቴሌብር 2', number: '0967386958', owner: 'Lwam Alem'},
    {bank: 'አዋሽ ባንክ 1', number: '01320877386700', owner: 'Marshalom Tesfay'},
    {bank: 'አዋሽ ባንክ 2', number: '01320779250100', owner: 'Lwam Alem'}
];
async function loadBanks() {
    const res = await fetch('/api/config/banks');
    let banks = await res.json();
    if (!banks || !banks.length) banks = DEFAULT_BANKS;
    const qrRes = await fetch('/api/config/bank_qr');
    const qr = await qrRes.json();
    const el = document.getElementById('banksList');
    el.innerHTML = banks.map(b => `
        <div class="card-box" style="cursor:default; text-align:left; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#b8a84a; font-weight:600; font-size:12px;">${b.bank}</div>
                <div style="color:#fff; font-size:14px; font-weight:700;">${b.number}</div>
                <div style="color:#8aa3b5; font-size:10px;">${b.owner}</div>
            </div>
            <button onclick="copyBankNumber('${b.number}', this)" style="background:#2b3a4a; border:none; color:#4a9eff; padding:6px 10px; border-radius:8px; font-size:10px;">📋 ኮፒ</button>
        </div>
    `).join('');
    if (qr) {
        el.innerHTML += `<div style="text-align:center; margin-top:10px;"><img src="${qr}" style="width:160px; border-radius:10px;" /><div style="font-size:10px; color:#8aa3b5; margin-top:4px;">QR ኮድ ተጠቅመው ይክፍሉ</div></div>`;
    }
}
function copyBankNumber(number, btn) {
    navigator.clipboard.writeText(number).then(() => {
        const original = btn.textContent;
        btn.textContent = '✅ ተኮፒዷል!';
        setTimeout(() => { btn.textContent = original; }, 1500);
    }).catch(() => {
        // Fallback for older webviews without clipboard API
        const ta = document.createElement('textarea');
        ta.value = number;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = '✅ ተኮፒዷል!';
        setTimeout(() => { btn.textContent = '📋 ኮፒ'; }, 1500);
    });
}

// ===== APPLICATIONS (Portfolio) =====
async function loadApplications() {
    const res = await fetch('/api/portfolio');
    const apps = await res.json();
    const el = document.getElementById('applicationsGrid');
    if (!apps.length) { el.innerHTML = '<p class="empty-msg">ገና ምንም Application የለም</p>'; return; }
    el.innerHTML = apps.map(a => `
        <div class="product-card">
            <img class="promo-img" src="${a.photo_url || '/static/logo.jpg'}" />
            <div class="info">
                <div class="card-name">${a.name}</div>
                ${a.file_url ? `<a href="${a.file_url}" target="_blank" class="ask-btn" style="display:block; text-decoration:none; box-sizing:border-box;">⬇️ አውርድ</a>` : ''}
            </div>
        </div>
    `).join('');
}

// ===== FEEDBACK / TESTIMONIALS / INBOX =====
async function loadTestimonials() {
    const res = await fetch('/api/testimonials');
    const items = await res.json();
    const el = document.getElementById('testimonialsList');
    if (!items.length) { el.innerHTML = '<p class="empty-msg">ገና ምንም አስተያየት የለም</p>'; return; }
    el.innerHTML = items.map(t => `
        <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:6px; border-left:3px solid #b8a84a;">
            <div style="color:#b8a84a; font-size:11px; font-weight:600;">${t.name} ${t.username ? '(@'+t.username+')' : ''}</div>
            <div style="color:#c0d8e8; font-size:11px; margin-top:2px;">${t.message}</div>
        </div>
    `).join('');
}
async function submitTestimonial() {
    const message = document.getElementById('testimonialInput').value.trim();
    if (!message) return;
    await fetch('/api/testimonials/add', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({initData, message})
    });
    document.getElementById('testimonialInput').value = '';
    loadTestimonials();
    alert('🙏 አመሰግናለሁ! አስተያየትዎ ታይቷል።');
}
async function submitPrivateMessage() {
    const message = document.getElementById('privateMessageInput').value.trim();
    if (!message) return;
    await fetch('/api/message/send', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({initData, recipient_type: 'admin', message})
    });
    document.getElementById('privateMessageInput').value = '';
    alert('✅ መልእክትዎ ተልኳል!');
}

// ===== SHARE =====
function shareChannel() {
    const channelUrl = 'https://t.me/MarshalomTech';
    tg.openTelegramLink('https://t.me/share/url?url=' + encodeURIComponent(channelUrl) + '&text=' + encodeURIComponent('Shalom Technology - CCTV and Electronics'));
}
document.getElementById('shareWhatsapp') && (document.getElementById('shareWhatsapp').href = 'https://wa.me/?text=' + encodeURIComponent('Check out Shalom Technology: https://t.me/MarshalomTech'));
document.getElementById('shareFacebook') && (document.getElementById('shareFacebook').href = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent('https://t.me/MarshalomTech'));
document.getElementById('shareTelegram') && (document.getElementById('shareTelegram').href = 'https://t.me/share/url?url=' + encodeURIComponent('https://t.me/MarshalomTech'));
document.getElementById('shareTwitter') && (document.getElementById('shareTwitter').href = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent('Check out Shalom Technology: https://t.me/MarshalomTech'));

// ===== AI CHAT (in-app, not redirecting to Telegram) =====
function addChatBubble(text, isUser) {
    const win = document.getElementById('aiChatWindow');
    const bubble = document.createElement('div');
    bubble.style.cssText = `max-width:80%; padding:8px 10px; border-radius:12px; font-size:11px; line-height:1.5; white-space:pre-line; ${isUser ? 'align-self:flex-end; background:#4a9eff; color:#fff;' : 'align-self:flex-start; background:#232e3c; color:#e0edf5;'}`;
    bubble.textContent = text;
    win.appendChild(bubble);
    win.scrollTop = win.scrollHeight;
}
async function sendAIMessage() {
    const input = document.getElementById('aiInput');
    const message = input.value.trim();
    if (!message) return;
    addChatBubble(message, true);
    input.value = '';
    addChatBubble('⏳...', false);
    const win = document.getElementById('aiChatWindow');
    const res = await fetch('/api/ai_chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({initData, message})
    });
    const data = await res.json();
    win.removeChild(win.lastChild);
    addChatBubble(data.reply || 'Error', false);
}

// ===== LOGIN (routes to team leader or employee page based on role) =====
async function doLogin() {
    const t = translations[currentLang];
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const res = await fetch('/api/employee/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    if (!data.ok) {
        document.getElementById('loginMsg').textContent = t.wrongLogin;
        return;
    }
    if (data.profile.role === 'team_leader') {
        teamLeaderCreds = {tl_username: username, tl_password: password};
        showPage('page-teamleader');
        renderTeamLeaderPanel(data.profile, username, password);
    } else {
        showPage('page-employee');
        renderEmployeePanel(data.profile, username, password);
    }
}

// ===== EMPLOYEE direct login (from Employee menu page) =====
async function employeeLogin() {
    const t = translations[currentLang];
    const username = document.getElementById('empUsername').value;
    const password = document.getElementById('empPassword').value;
    const res = await fetch('/api/employee/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    if (!data.ok) { document.getElementById('empMsg').textContent = t.wrongLogin; return; }
    if (data.profile.role === 'team_leader') {
        alert(currentLang === 'en' ? 'This is a Team Leader account - please use the Team Leader menu.' : 'ይህ የቲም ሊደር አካውንት ነው - እባክዎ የቲም ሊደር ምናሌ ይጠቀሙ።');
        return;
    }
    renderEmployeePanel(data.profile, username, password);
}

function renderEmployeePanel(profile, username, password) {
    const t = translations[currentLang];
    document.getElementById('empLoginBox').style.display = 'none';
    const el = document.getElementById('empContent');
    el.style.display = 'block';

    if (profile.must_change_password) {
        el.innerHTML = `
            <div style="background:rgba(255,255,255,0.03); border-radius:14px; padding:14px; text-align:center;">
                <div style="font-size:28px;">🔐</div>
                <p style="color:#ffb84a; font-size:12px; margin:6px 0;">${t.mustChangePw}</p>
                <input type="password" id="newPwInput" placeholder="New password" class="input-field">
                <button class="btn-primary" onclick="changeEmpPassword('${username}','${password}')">${t.setPwBtn}</button>
                <div id="pwMsg" style="font-size:11px; margin-top:6px; color:#4aff8a;"></div>
            </div>
        `;
        return;
    }

    el.innerHTML = `
        <div style="background:rgba(255,255,255,0.04); border-radius:14px; padding:14px;">
            <div style="text-align:center;">${profile.profile_photo ? `<img src="${profile.profile_photo}" style="width:64px; height:64px; border-radius:50%; object-fit:cover;">` : '<span style="font-size:32px;">👤</span>'}</div>
            <div style="text-align:center; color:#fff; font-weight:700; font-size:14px;">${profile.full_name}</div>
            <div style="text-align:center; color:#8aa3b5; font-size:11px; margin-bottom:8px;">${profile.position} - ${profile.internal_email || ''}</div>
            <div style="font-size:11px; color:#c0d8e8; line-height:1.8;">
                <b>💰 ደመወዝ:</b> ${profile.salary || '-'}<br>
                <b>🎁 ቦነስ:</b><br>${(profile.bonus || 'የለም').replace(
/g,'<br>')}<br>
                <b>⚠️ ማስጠንቀቂያ:</b><br>${(profile.warnings || 'የለም').replace(/
/g,'<br>')}<br>
                <b>📋 ስራዎች:</b><br>${(profile.tasks || 'የለም').replace(/
/g,'<br>')}
            </div>
            <div style="margin-top:10px; font-size:9px; color:#8aa3b5;">📷 የመገለጫ ፎቶ ቀይር:</div>
            <input type="file" id="empPhotoFile" accept="image/*" class="input-field" style="padding:6px;">
            <button class="btn-primary" onclick="empSavePhoto('${username}', ${JSON.stringify(password)})">💾 ፎቶ አስቀምጥ</button>
            <div class="section-title" style="margin-top:10px;">📩 መልእክቶቼ</div>
            <button class="btn-primary" onclick="empLoadInbox('${username}', ${JSON.stringify(password)})">🔄 አሳይ</button>
            <div id="empInboxList"></div>
        </div>
    `;
}
async function empSavePhoto(username, password) {
    const fileInput = document.getElementById('empPhotoFile');
    if (!fileInput.files || !fileInput.files[0]) { alert('ፎቶ ይምረጡ'); return; }
    const photo = await fileToBase64(fileInput.files[0]);
    await fetch(`/api/team/employees/${username}/photo`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({tl_username: username, tl_password: password, photo})
    });
    alert('✅ ፎቶ ተቀምጧል!');
    employeeLoginRetry(username, password);
}
async function empLoadInbox(username, password) {
    const res = await fetch('/api/message/inbox', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({tl_username: username, tl_password: password})
    });
    const items = await res.json();
    document.getElementById('empInboxList').innerHTML = (items || []).map(m => `
        <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:4px; font-size:10px;">
            <b>${m.sender_name}</b><br>${m.message}<br><span style="color:#8aa3b5;">${m.created_at}</span>
        </div>
    `).join('') || '<p class="empty-msg">ምንም መልእክት የለም</p>';
}

async function changeEmpPassword(username, oldPassword) {
    const newPassword = document.getElementById('newPwInput').value;
    if (!newPassword) return;
    const res = await fetch('/api/employee/set_password', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({username, old_password: oldPassword, new_password: newPassword})
    });
    const data = await res.json();
    if (data.ok) {
        document.getElementById('pwMsg').textContent = translations[currentLang].pwChanged;
        setTimeout(() => employeeLoginRetry(username, newPassword), 1000);
    }
}
async function employeeLoginRetry(username, password) {
    const res = await fetch('/api/employee/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    if (data.ok) renderEmployeePanel(data.profile, username, password);
}

// ===== TEAM LEADER =====
async function teamLeaderLogin() {
    const t = translations[currentLang];
    const username = document.getElementById('tlUsername').value;
    const password = document.getElementById('tlPassword').value;
    const res = await fetch('/api/employee/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    if (!data.ok || data.profile.role !== 'team_leader') {
        document.getElementById('tlMsg').textContent = t.wrongLogin;
        return;
    }
    teamLeaderCreds = {tl_username: username, tl_password: password};
    renderTeamLeaderPanel(data.profile, username, password);
}

async function renderTeamLeaderPanel(profile) {
    document.getElementById('tlLoginBox').style.display = 'none';
    const el = document.getElementById('tlContent');
    el.style.display = 'block';
    el.innerHTML = `<p class="empty-msg">⏳...</p>`;

    const res = await fetch('/api/team/employees', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(teamLeaderCreds)
    });
    const employees = await res.json();

    el.innerHTML = `
        <div style="text-align:center; margin-bottom:10px;">
            ${profile.profile_photo ? `<img src="${profile.profile_photo}" style="width:60px; height:60px; border-radius:50%; object-fit:cover; margin-bottom:6px;">` : '<div style="font-size:28px;">👔</div>'}
            <div style="color:#fff; font-weight:700;">${profile.full_name}</div>
            <div style="color:#8aa3b5; font-size:11px;">🌟 ቲም ሊደር | ${profile.internal_email || ''}</div>
        </div>

        <div class="section-title">➕ አዲስ ሰራተኛ ጨምር</div>
        <input type="text" id="tlNewName" placeholder="ሙሉ ስም" class="input-field">
        <input type="text" id="tlNewPosition" placeholder="ስራ" class="input-field">
        <button class="btn-primary gold" onclick="tlAddEmployee()">➕ ጨምር</button>

        <div class="section-title" style="margin-top:12px;">👥 ሰራተኞቼ</div>
        <div id="tlEmployeeList"></div>

        <div class="section-title" style="margin-top:12px;">📩 መልእክቶቼ</div>
        <button class="btn-primary" onclick="tlLoadInbox()">🔄 መልእክቶች አሳይ</button>
        <div id="tlInboxList"></div>
    `;
    const listEl = document.getElementById('tlEmployeeList');
    listEl.innerHTML = (employees || []).map(e => `
        <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:8px; margin-bottom:6px;">
            <div style="display:flex; align-items:center; gap:8px;">
                ${e.profile_photo ? `<img src="${e.profile_photo}" style="width:32px; height:32px; border-radius:50%; object-fit:cover;">` : '<span style="font-size:20px;">👤</span>'}
                <div><b style="color:#fff; font-size:12px;">${e.full_name}</b><br><span style="color:#8aa3b5; font-size:9px;">${e.position} • ${e.internal_email || ''}</span></div>
            </div>
            <div style="display:flex; gap:4px; margin-top:6px; flex-wrap:wrap;">
                <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="tlResetPassword('${e.username}')">🔐 Reset</button>
                <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="tlAssignTask('${e.username}')">📋 Task</button>
                <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="tlGiveBonus('${e.username}')">🎁 Bonus</button>
                <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#5a2a2a; color:#fff;" onclick="tlDeleteEmployee('${e.username}')">🗑️ ሰርዝ</button>
            </div>
        </div>
    `).join('') || '<p class="empty-msg">ምንም ሰራተኛ የለም</p>';
}

async function tlAddEmployee() {
    const full_name = document.getElementById('tlNewName').value;
    const position = document.getElementById('tlNewPosition').value;
    if (!full_name) { alert('ስም ያስፈልጋል'); return; }
    const res = await fetch('/api/team/add_employee', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({...teamLeaderCreds, full_name, position, role: 'employee'})
    });
    const data = await res.json();
    if (data.ok) {
        alert(`✅ ተጨምሯል!
Username: ${data.username}
Password: ${data.password}
Email: ${data.internal_email}

⚠️ ሰራተኛው መጀመሪያ ቦቱን /start ካደረገ በኋላ ብቻ በራስ-ሰር ማሳወቅ ይቻላል።`);
        teamLeaderLoginRefresh();
    }
}
async function teamLeaderLoginRefresh() {
    const res = await fetch('/api/employee/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: teamLeaderCreds.tl_username, password: teamLeaderCreds.tl_password})
    });
    const data = await res.json();
    if (data.ok) renderTeamLeaderPanel(data.profile);
}
async function tlDeleteEmployee(username) {
    if (!confirm('እርግጠኛ ነዎት?')) return;
    await fetch('/api/team/employees/'+username, {
        method: 'DELETE', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(teamLeaderCreds)
    });
    teamLeaderLoginRefresh();
}
async function tlLoadInbox() {
    const res = await fetch('/api/message/inbox', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(teamLeaderCreds)
    });
    const items = await res.json();
    document.getElementById('tlInboxList').innerHTML = (items || []).map(m => `
        <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:4px; font-size:10px;">
            <b>${m.sender_name}</b> (@${m.sender_username || 'የለም'})<br>${m.message}<br><span style="color:#8aa3b5;">${m.created_at}</span>
        </div>
    `).join('') || '<p class="empty-msg">ምንም መልእክት የለም</p>';
}

async function tlResetPassword(username) {
    const res = await fetch('/api/team/reset_password', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({...teamLeaderCreds, username})
    });
    const data = await res.json();
    if (data.ok) alert('✅ Temp password: ' + data.temp_password);
}
async function tlAssignTask(username) {
    const task = prompt('📋 New task:');
    if (!task) return;
    await fetch('/api/team/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({...teamLeaderCreds, username, field: 'tasks', value: task})
    });
    alert('✅ Task assigned!');
}
async function tlGiveBonus(username) {
    const bonus = prompt('🎁 Bonus amount:');
    if (!bonus) return;
    await fetch('/api/team/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({...teamLeaderCreds, username, field: 'bonus', value: bonus})
    });
    alert('✅ Bonus added!');
}

// ===== ADMIN (auto-detected via Telegram identity, no manual login) =====
async function loadAdminPage() {
    const el = document.getElementById('adminContent');
    const verifyRes = await fetch('/api/admin/verify', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({initData})
    });
    const verify = await verifyRes.json();
    if (!verify.ok) {
        el.innerHTML = '<p class="empty-msg">🚫 ተደራሽነት የለዎትም (የባለቤት አካውንት ብቻ)</p>';
        return;
    }
    const [statsRes, productsRes, customersRes, jobsRes, appsRes, banksRes, employeesRes] = await Promise.all([
        fetch('/api/admin/stats', {headers:{'X-Init-Data': initData}}),
        fetch('/api/products'),
        fetch('/api/admin/customers', {headers:{'X-Init-Data': initData}}),
        fetch('/api/jobs'),
        fetch('/api/admin/applications', {headers:{'X-Init-Data': initData}}),
        fetch('/api/config/banks'),
        fetch('/api/team/employees', {method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData}, body: JSON.stringify({})})
    ]);
    const stats = await statsRes.json();
    const products = await productsRes.json();
    const customers = await customersRes.json();
    const jobs = await jobsRes.json();
    const applications = await appsRes.json();
    const banks = await banksRes.json();
    const allEmployees = await employeesRes.json();

    el.innerHTML = `
        <div class="grid2" style="margin-bottom:10px;">
            <div class="stat-box"><div class="stat-num">${stats.customers}</div><div class="stat-label">👥 ደንበኞች</div></div>
            <div class="stat-box"><div class="stat-num">${stats.messages}</div><div class="stat-label">💬 መልእክቶች</div></div>
            <div class="stat-box"><div class="stat-num">${stats.price_inquiries}</div><div class="stat-label">💰 የዋጋ ጥያቄ</div></div>
            <div class="stat-box"><div class="stat-num">${stats.products}</div><div class="stat-label">🛍️ ምርቶች</div></div>
        </div>
        <div class="section-title">🛍️ ምርት ጨምር</div>
        <input type="text" id="newProdName" placeholder="የምርት ስም" class="input-field">
        <input type="text" id="newProdCat" placeholder="ምድብ (CCTV/ኤሌክትሮኒክስ)" class="input-field">
        <textarea id="newProdDesc" placeholder="መግለጫ" class="input-field" rows="2"></textarea>
        <input type="text" id="newProdLink" placeholder="🔗 የፎቶ ሊንክ (አማራጭ)" class="input-field">
        <div style="text-align:center; color:#8aa3b5; font-size:10px; margin:4px 0;">-- ወይም --</div>
        <input type="file" id="newProdFile" accept="image/*" class="input-field" style="padding:6px;">
        <button class="btn-primary gold" onclick="adminAddProduct()">➕ ምርት ጨምር</button>
        <div id="adminProdList" style="margin-top:8px;">
            ${products.map(p => `
                <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:6px 8px; margin-bottom:4px; font-size:11px; display:flex; justify-content:space-between; align-items:center;">
                    <span>${p.name} (${p.category})</span>
                    <span style="color:#ff6b6b; cursor:pointer;" onclick="adminDeleteProduct(${p.id})">🗑️</span>
                </div>
            `).join('')}
        </div>
        <div class="section-title" style="margin-top:14px;">💼 ስራ ጨምር</div>
        <input type="text" id="newJobTitle" placeholder="የስራ ርዕስ" class="input-field">
        <input type="text" id="newJobLoc" placeholder="ቦታ" class="input-field">
        <textarea id="newJobDesc" placeholder="መግለጫ" class="input-field" rows="2"></textarea>
        <div style="font-size:9px; color:#8aa3b5; margin:4px 0;">📄 PDF ዝርዝር (አማራጭ):</div>
        <input type="file" id="newJobPdf" accept="application/pdf" class="input-field" style="padding:6px;">
        <button class="btn-primary gold" onclick="adminAddJob()">➕ ስራ ጨምር</button>
        <div id="adminJobList" style="margin-top:8px;">
            ${jobs.map(j => `
                <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:6px 8px; margin-bottom:4px; font-size:11px; display:flex; justify-content:space-between; align-items:center;">
                    <span>${j.title}</span>
                    <span style="color:#ff6b6b; cursor:pointer;" onclick="adminDeleteJob(${j.id})">🗑️</span>
                </div>
            `).join('')}
        </div>
        <div class="section-title" style="margin-top:14px;">👥 ደንበኞች (የቅርብ ጊዜ)</div>
        <div>
            ${customers.slice(0,10).map(c => `
                <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:6px 8px; margin-bottom:4px; font-size:10px;">
                    👤 ${c.name || 'ስም የለም'} (@${c.username || 'የለም'}) - 💬 ${c.message_count}
                </div>
            `).join('')}
        </div>

        <div class="section-title" style="margin-top:14px;">📋 የስራ ማመልከቻዎች</div>
        <div>
            ${applications.filter(a => a.status === 'pending').map(a => `
                <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:6px; font-size:10px;">
                    👤 ${a.name} (@${a.username || 'የለም'})<br>
                    💼 ${a.job_title} | 📞 ${a.phone} | ✉️ ${a.email || '-'}<br>
                    <div style="display:flex; gap:4px; margin-top:6px;">
                        <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#2a5a3a; color:#fff;" onclick="adminApproveApp(${a.id})">✅ አጽድቅ</button>
                        <button style="flex:1; font-size:9px; padding:5px; border:none; border-radius:6px; background:#5a2a2a; color:#fff;" onclick="adminRejectApp(${a.id})">❌ አትቀበል</button>
                    </div>
                </div>
            `).join('') || '<p class="empty-msg">ምንም አዲስ ማመልከቻ የለም</p>'}
        </div>

        <div class="section-title" style="margin-top:14px;">🏦 የባንክ ሂሳብ አስተዳደር</div>
        <textarea id="banksConfigText" class="input-field" rows="6" style="font-size:10px;">${JSON.stringify(banks && banks.length ? banks : DEFAULT_BANKS, null, 2)}</textarea>
        <button class="btn-primary gold" onclick="adminSaveBanks()">💾 ባንክ መረጃ አስቀምጥ</button>
        <div style="font-size:9px; color:#8aa3b5; margin:4px 0;">📷 QR ኮድ ፎቶ:</div>
        <input type="file" id="bankQrFile" accept="image/*" class="input-field" style="padding:6px;">
        <button class="btn-primary gold" onclick="adminSaveBankQr()">💾 QR አስቀምጥ</button>

        <div class="section-title" style="margin-top:14px;">🏠 የመነሻ ገጽ ማስተካከያ</div>
        <div style="font-size:9px; color:#8aa3b5; margin-bottom:4px;">ራስጌ ምርጫ:</div>
        <select id="homeHeaderMode" class="input-field">
            <option value="text">✨ ጽሁፍ (Shalom Technology + blink)</option>
            <option value="phone">📞 ስልክ ቁጥር (አኒሜሽን)</option>
        </select>
        <div style="font-size:9px; color:#8aa3b5; margin:4px 0;">🖼️ ጀርባ ፎቶ 1:</div>
        <input type="file" id="homeBg1" accept="image/*" class="input-field" style="padding:6px;">
        <div style="font-size:9px; color:#8aa3b5; margin:4px 0;">🖼️ ጀርባ ፎቶ 2 (አማራጭ):</div>
        <input type="file" id="homeBg2" accept="image/*" class="input-field" style="padding:6px;">
        <button class="btn-primary gold" onclick="adminSaveHomeSettings()">💾 የመነሻ ገጽ አስቀምጥ</button>

        <div class="section-title" style="margin-top:14px;">📱 Applications አስተዳደር</div>
        <input type="text" id="newAppName" placeholder="የApp ስም" class="input-field">
        <input type="file" id="newAppPhoto" accept="image/*" class="input-field" style="padding:6px;">
        <input type="file" id="newAppFile" class="input-field" style="padding:6px;">
        <button class="btn-primary gold" onclick="adminAddApplication()">➕ App ጨምር</button>
        <div id="adminAppList"></div>

        <div class="section-title" style="margin-top:14px;">🌐 ማህበራዊ ሚዲያ አስተካክል</div>
        <textarea id="socialConfigText" class="input-field" rows="6" style="font-size:10px;">${JSON.stringify(DEFAULT_SOCIAL, null, 2)}</textarea>
        <button class="btn-primary gold" onclick="adminSaveSocial()">💾 ማህበራዊ ሚዲያ አስቀምጥ</button>

        <div class="section-title" style="margin-top:14px;">🌟 ምስክርነቶች አስተዳደር</div>
        <button class="btn-primary" onclick="adminLoadTestimonialsMod()">🔄 አሳይ</button>
        <div id="adminTestimonialsMod"></div>

        <div class="section-title" style="margin-top:14px;">👥 ሰራተኞች/ቲም ሊደር አስተዳደር</div>
        <div id="adminEmployeesList">
            ${(allEmployees || []).map(e => `
                <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:4px; font-size:10px;">
                    <b>${e.full_name}</b> (${e.role === 'team_leader' ? '🌟 ቲም ሊደር' : '👤 ሰራተኛ'})<br>${e.position} • ${e.internal_email || ''}
                    <div style="display:flex; gap:4px; margin-top:4px;">
                        <button style="flex:1; font-size:9px; padding:4px; border:none; border-radius:6px; background:#2b3a4a; color:#fff;" onclick="adminResetEmpPassword('${e.username}')">🔐 Reset</button>
                        <button style="flex:1; font-size:9px; padding:4px; border:none; border-radius:6px; background:#5a2a2a; color:#fff;" onclick="adminDeleteEmployee('${e.username}')">🗑️ ሰርዝ</button>
                    </div>
                </div>
            `).join('') || '<p class="empty-msg">ምንም የለም</p>'}
        </div>

        <div class="section-title" style="margin-top:14px;">📩 የመልእክት ሳጥን (ሁሉም)</div>
        <button class="btn-primary" onclick="adminLoadInbox()">🔄 መልእክቶች አሳይ</button>
        <div id="adminInboxList"></div>

        <div class="section-title" style="margin-top:14px;">🔐 አድሚን / ቲም ሊደር ፍጠር</div>
        <input type="text" id="newCredName" placeholder="ሙሉ ስም" class="input-field">
        <input type="text" id="newCredPosition" placeholder="ስራ/ደረጃ" class="input-field">
        <select id="newCredRole" class="input-field">
            <option value="employee">👤 ሰራተኛ</option>
            <option value="team_leader">🌟 ቲም ሊደር</option>
        </select>
        <button class="btn-primary gold" onclick="adminGenerateCredentials()">🔑 Username/Password ፍጠር</button>
        <div id="credResult" style="font-size:11px; margin-top:6px; color:#4aff8a;"></div>
    `;
}

async function adminApproveApp(id) {
    await fetch(`/api/admin/applications/${id}/approve`, {method:'POST', headers:{'X-Init-Data': initData}});
    loadAdminPage();
}
async function adminRejectApp(id) {
    await fetch(`/api/admin/applications/${id}/reject`, {method:'POST', headers:{'X-Init-Data': initData}});
    loadAdminPage();
}
async function adminSaveBanks() {
    try {
        const value = JSON.parse(document.getElementById('banksConfigText').value);
        await fetch('/api/admin/config/banks', {
            method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
            body: JSON.stringify({value})
        });
        alert('✅ ተቀምጧል!');
        loadBanks();
    } catch(e) { alert('❌ JSON ትክክል አይደለም'); }
}
async function adminSaveBankQr() {
    const fileInput = document.getElementById('bankQrFile');
    if (!fileInput.files || !fileInput.files[0]) { alert('ፎቶ ይምረጡ'); return; }
    const base64 = await fileToBase64(fileInput.files[0]);
    await fetch('/api/admin/config/bank_qr', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({value: base64})
    });
    alert('✅ QR ተቀምጧል!');
    loadBanks();
}
async function adminAddApplication() {
    const name = document.getElementById('newAppName').value;
    const photoInput = document.getElementById('newAppPhoto');
    const fileInput = document.getElementById('newAppFile');
    if (!name) { alert('ስም ያስፈልጋል'); return; }
    let photo_url = null, file_url = null;
    if (photoInput.files && photoInput.files[0]) photo_url = await fileToBase64(photoInput.files[0]);
    if (fileInput.files && fileInput.files[0]) file_url = await fileToBase64(fileInput.files[0]);
    await fetch('/api/admin/portfolio', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({name, photo_url, file_url})
    });
    alert('✅ ተጨምሯል!');
    loadApplications();
    loadAdminPage();
}
async function adminSaveHomeSettings() {
    const header_mode = document.getElementById('homeHeaderMode').value;
    const bg1 = document.getElementById('homeBg1');
    const bg2 = document.getElementById('homeBg2');
    const existingRes = await fetch('/api/config/home_settings');
    const existing = await existingRes.json() || {};
    const bg_photos = [];
    if (bg1.files && bg1.files[0]) bg_photos.push(await fileToBase64(bg1.files[0]));
    if (bg2.files && bg2.files[0]) bg_photos.push(await fileToBase64(bg2.files[0]));
    const value = {header_mode, bg_photos: bg_photos.length ? bg_photos : (existing.bg_photos || [])};
    await fetch('/api/admin/config/home_settings', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({value})
    });
    alert('✅ ተቀምጧል!');
    loadHomeSettings();
}
async function adminSaveSocial() {
    try {
        const value = JSON.parse(document.getElementById('socialConfigText').value);
        await fetch('/api/admin/config/social', {
            method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
            body: JSON.stringify({value})
        });
        alert('✅ ተቀምጧል!');
        loadSocial();
    } catch(e) { alert('❌ JSON ትክክል አይደለም'); }
}
async function adminLoadTestimonialsMod() {
    const res = await fetch('/api/testimonials');
    const items = await res.json();
    document.getElementById('adminTestimonialsMod').innerHTML = (items || []).map(t => `
        <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:6px 8px; margin-bottom:4px; font-size:10px; display:flex; justify-content:space-between; align-items:center;">
            <span><b>${t.name}</b>: ${t.message}</span>
            <span style="color:#ff6b6b; cursor:pointer;" onclick="adminDeleteTestimonial(${t.id})">🗑️</span>
        </div>
    `).join('') || '<p class="empty-msg">ምንም የለም</p>';
}
async function adminDeleteTestimonial(id) {
    await fetch('/api/testimonials/'+id, {method:'DELETE', headers:{'Content-Type':'application/json','X-Init-Data': initData}, body: JSON.stringify({})});
    adminLoadTestimonialsMod();
    loadTestimonials();
}
async function adminResetEmpPassword(username) {
    const res = await fetch('/api/team/reset_password', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({username})
    });
    const data = await res.json();
    if (data.ok) alert('✅ Temp password: ' + data.temp_password);
}
async function adminDeleteEmployee(username) {
    if (!confirm('እርግጠኛ ነዎት?')) return;
    await fetch('/api/team/employees/'+username, {method:'DELETE', headers:{'Content-Type':'application/json','X-Init-Data': initData}, body: JSON.stringify({})});
    loadAdminPage();
}
async function adminLoadInbox() {
    const res = await fetch('/api/message/inbox', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({})
    });
    const items = await res.json();
    document.getElementById('adminInboxList').innerHTML = (items || []).map(m => `
        <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:4px; font-size:10px;">
            <b>${m.sender_name}</b> (@${m.sender_username || 'የለም'}) → ${m.recipient_type}<br>${m.message}<br><span style="color:#8aa3b5;">${m.created_at}</span>
        </div>
    `).join('') || '<p class="empty-msg">ምንም መልእክት የለም</p>';
}
async function adminGenerateCredentials() {
    const full_name = document.getElementById('newCredName').value;
    const position = document.getElementById('newCredPosition').value;
    const role = document.getElementById('newCredRole').value;
    if (!full_name) { alert('ስም ያስፈልጋል'); return; }
    const res = await fetch('/api/admin/generate_credentials', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({full_name, position, role})
    });
    const data = await res.json();
    if (data.ok) {
        document.getElementById('credResult').innerHTML = `✅ Username: <b>${data.username}</b><br>✅ Password: <b>${data.password}</b>`;
    }
}

async function adminAddProduct() {
    const name = document.getElementById('newProdName').value;
    const category = document.getElementById('newProdCat').value;
    const description = document.getElementById('newProdDesc').value;
    const linkUrl = document.getElementById('newProdLink').value;
    const fileInput = document.getElementById('newProdFile');
    if (!name || !category) { alert('ስም እና ምድብ ያስፈልጋል'); return; }

    let photo_url = linkUrl;
    if (fileInput.files && fileInput.files[0]) {
        photo_url = await fileToBase64(fileInput.files[0]);
    }
    await fetch('/api/admin/products', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({name, category, description, photo_url})
    });
    loadAdminPage();
    loadProducts();
}
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}
async function adminDeleteProduct(id) {
    await fetch('/api/admin/products/'+id, {method:'DELETE', headers:{'X-Init-Data': initData}});
    loadAdminPage();
    loadProducts();
}
async function adminAddJob() {
    const title = document.getElementById('newJobTitle').value;
    const location = document.getElementById('newJobLoc').value;
    const description = document.getElementById('newJobDesc').value;
    const pdfInput = document.getElementById('newJobPdf');
    if (!title) { alert('የስራ ርዕስ ያስፈልጋል'); return; }
    let pdf_url = null;
    if (pdfInput.files && pdfInput.files[0]) pdf_url = await fileToBase64(pdfInput.files[0]);
    await fetch('/api/admin/jobs', {
        method:'POST', headers:{'Content-Type':'application/json','X-Init-Data': initData},
        body: JSON.stringify({title, location, description, pdf_url})
    });
    loadAdminPage();
    loadJobs();
}
async function adminDeleteJob(id) {
    await fetch('/api/admin/jobs/'+id, {method:'DELETE', headers:{'X-Init-Data': initData}});
    loadAdminPage();
    loadJobs();
}

// ===== INIT =====
loadProducts();
loadJobs();
loadPromos();
loadBanks();
loadApplications();
loadTestimonials();
loadSocial();
loadHomeSettings();
setInterval(maybeRotateProducts, 60000);
if (window.location.hash) {
    const targetPage = window.location.hash.replace('#', '');
    if (document.getElementById(targetPage)) showPage(targetPage);
}
</script>
</body>
</html>
