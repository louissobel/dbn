import React from 'react';

const StatusDot = function({error, pending, ok}) {
  var status = "";
  if (error) {
    status = "error"
  } else if (pending) {
    status = "pending"
  } else if (ok) {
    status = "ok"
  }

  return (
    <div className={"dbnft-status-dot " + status} />
  )
}


export default StatusDot;