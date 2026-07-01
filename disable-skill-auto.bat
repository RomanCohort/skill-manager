@echo off
REM Disable Skill Manager Auto-Activation

cd /d %USERPROFILE%\.claude\skill-manager\data

echo.
echo ========================================
echo   Skill Manager - Disable Auto-Activation
echo ========================================
echo.

REM Update config.json
echo Updating config.json...
(
echo {
echo   "auto_activation_enabled": false,
echo   "default_choice": "never",
echo   "session_count": 1,
echo   "last_session": null,
echo   "activation_strategy": "balanced",
echo   "user_preferences": {
echo     "favorite_skills": [],
echo     "disabled_skills": []
echo   }
echo }
) > config.json

echo.
echo [OK] Auto-activation DISABLED
echo.
echo Skill Manager will run silently.
echo Use CLI for manual skill management:
echo   python skill_manager.py recommend "<prompt>"
echo.
echo To re-enable, run: enable-skill-auto.bat
echo.

pause