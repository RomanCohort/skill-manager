@echo off
REM Skill Manager CLI for Windows
REM Usage: skill.bat <command> [options]

cd /d %USERPROFILE%\.claude\skill-manager
python skill_manager.py %*