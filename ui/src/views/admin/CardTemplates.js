import React from "react";
import CardTemplates from "components/Search/CardTemplates/index";

export default function CardTemplatesView() {
    return (
        <>
            <div className="flex flex-wrap mh-full">
                <div className="w-full mb-12 px-4">
                    <CardTemplates />
                </div>
            </div>
        </>
    );
}
