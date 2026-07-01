@echo off
REM Enable Skill Manager Auto-Activation

cd /d %USERPROFILE%\.claude\skill-manager\data

echo.
echo ========================================
echo   Skill Manager - Enable Auto-Activation
echo ========================================
echo.

REM Update config.json
echo Updating config.json...
(
echo {
echo   "auto_activation_enabled": true,
echo   "default_choice": "always",
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
echo [OK] Auto-activation ENABLED
echo.
echo Next session will automatically:
echo   - Analyze your prompts
echo   - Recommend relevant skills
echo   - Show activation suggestions
echo.
echo To disable, run: disable-skill-auto.bat
echo.

pause