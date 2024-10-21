"use client"

import React from "react";
import { usePublicInfoQuery } from "../utils/queries/public-info";

export function ServerName() {
  const [publicInfo] = usePublicInfoQuery();

  return (
      <React.Fragment>{publicInfo.name.name}</React.Fragment>
  );
}
