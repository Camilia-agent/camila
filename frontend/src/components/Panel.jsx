export default function Panel({
  title,
  ptag,
  action,
  onAction,
  withCornerTip,
  children,
  headerExtra,
  bodyStyle,
  className = ''
}) {
  const classes = ['panel'];
  if (withCornerTip) classes.push('panel-with-corner-tip');
  if (className)     classes.push(className);

  return (
    <div className={classes.join(' ')}>
      <div className="panel-header">
        <div className="panel-title">
          {title}
          {ptag ? <span className="ptag">{ptag}</span> : null}
        </div>
        {headerExtra}
        {action ? (
          <button className="panel-action" type="button" onClick={onAction}>
            {action}
          </button>
        ) : null}
      </div>
      <div className="panel-body" style={bodyStyle}>{children}</div>
    </div>
  );
}
