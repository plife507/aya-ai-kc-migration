# KC Heartbeat

On heartbeat, keep routine checks quiet unless there is a meaningful state change, an automatic repair, or a real blocker.

## Slack Gateway Watchdog

KC must keep the Slack listener available for connected KC channels, including `#pp-dispatch-mgmt`.

Run the configured watchdog instead of hand-checking status:

```bash
/home/plife507/AYA-CLAW/scripts/kc-slack-gateway-watchdog
```

Schedule: OpenClaw cron job `kc-slack-gateway-watchdog`, every hour.

Expected behavior:
- Check `openclaw channels status --json` for Slack account `default`.
- Healthy means Slack is enabled, configured, running, connected, and not restart-pending.
- If Slack is unhealthy, restart the OpenClaw gateway once, then re-check.
- Stay silent when healthy.
- Notify Nathan only if the watchdog restarted the gateway successfully or Slack remains unhealthy after the restart.
- Do not post into Slack as part of this check.
