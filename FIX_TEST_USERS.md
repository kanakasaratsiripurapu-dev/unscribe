# Fix Test Users Access Issue

## Problem
OAuth works only for sjsu.edu emails, other test users can't sign in.

## Solution Steps

### 1. Check OAuth Consent Screen Publishing Status

1. Go to: https://console.cloud.google.com/apis/credentials/consent

2. **Publishing Status should be "Testing"** (not "In production")
   - If "In production", change to "Testing"
   - Production mode requires app verification
   - Testing mode allows approved test users

3. **User Type:**
   - Should be "External" (for personal Gmail accounts)
   - "Internal" only works for Google Workspace accounts

### 2. Add Test Users

1. Scroll to "Test users" section
2. Click "+ ADD USERS"
3. Add each email individually:
   - Sksarat2003@gmail.com
   - ganes.siri@gmail.com
   - manonag@gmail.com
   - svgteja@gmail.com
   - vagdevi.chalumuri@gmail.com
   - Any other emails you want to test with

4. Click "ADD" after each one

### 3. Remove Domain Restrictions (Important!)

1. In OAuth consent screen, check "Authorized domains"
2. If you see restrictions, either:
   - Remove domain restrictions, OR
   - Add "gmail.com" and other domains you need

3. Make sure there are NO email domain restrictions blocking Gmail

### 4. Verify Test Users List

1. Scroll to "Test users" section
2. Verify all emails are listed:
   - Each email should appear on its own line
   - No duplicates
   - All email addresses are correct (no typos)

### 5. Save and Wait

1. Click "SAVE" at the bottom
2. Wait 2-3 minutes for changes to propagate
3. Clear browser cache/cookies
4. Try logging in with test user email

### 6. If Still Not Working

**Check these common issues:**
- Is the email address spelled correctly in test users?
- Did you click "SAVE" after adding test users?
- Did you wait 2-3 minutes after saving?
- Are you using the exact email address (case-sensitive for domain)?
- Try using an incognito/private browser window

## Quick Checklist

- [ ] Publishing status is "Testing" (not "In production")
- [ ] User type is "External" 
- [ ] All test user emails are added
- [ ] No domain restrictions blocking Gmail
- [ ] Clicked "SAVE" after changes
- [ ] Waited 2-3 minutes
- [ ] Cleared browser cache
- [ ] Tried incognito window

